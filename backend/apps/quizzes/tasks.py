import logging
from celery import shared_task
from django.db import transaction

from .models import Quiz, Question, Choice
from .ai_service import GroqQuizGenerator

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def generate_quiz_questions(self, quiz_id: str):
    """
    Celery task that generates quiz questions asynchronously using Groq API.
    Updates the quiz status to 'ready' on success or 'failed' on failure.
    """
    try:
        quiz = Quiz.objects.get(id=quiz_id)
    except Quiz.DoesNotExist:
        logger.error(f"Quiz {quiz_id} not found for generation.")
        return

    # To avoid duplicate processing if celery retriggers
    if quiz.status == Quiz.Status.READY:
        logger.info(f"Quiz {quiz_id} is already ready.")
        return

    logger.info(f"Starting generation for Quiz {quiz_id} ('{quiz.topic}')")

    try:
        generator = GroqQuizGenerator()
        data = generator.generate(quiz.topic, quiz.question_count, quiz.difficulty)

        with transaction.atomic():
            # Clear existing questions if we are regenerating
            quiz.questions.all().delete()

            # Bulk create questions and choices
            questions_to_create = []
            for idx, q_data in enumerate(data['questions'], start=1):
                questions_to_create.append(
                    Question(
                        quiz=quiz,
                        order=idx,
                        question_text=q_data['question_text'],
                        explanation=q_data['explanation'],
                        points=q_data.get('points', 1),
                        question_type=Question.QuestionType.MCQ
                    )
                )

            # Insert all questions into DB
            created_questions = Question.objects.bulk_create(questions_to_create)

            # Prepare choices for bulk insert
            choices_to_create = []
            for question, q_data in zip(created_questions, data['questions']):
                for c_idx, c_data in enumerate(q_data['choices'], start=1):
                    choices_to_create.append(
                        Choice(
                            question=question,
                            choice_text=c_data['choice_text'],
                            is_correct=c_data['is_correct'],
                            order=c_idx
                        )
                    )

            # Insert all choices into DB
            Choice.objects.bulk_create(choices_to_create)

            # Mark ready
            quiz.status = Quiz.Status.READY
            quiz.error_message = ""
            quiz.ai_model_used = "groq-llama-3.3-70b-versatile"
            quiz.save(update_fields=['status', 'error_message', 'ai_model_used', 'updated_at'])

        logger.info(f"Successfully generated Quiz {quiz_id}")

    except Exception as exc:
        logger.error(f"Failed to generate Quiz {quiz_id}: {str(exc)}")
        quiz.status = Quiz.Status.FAILED
        quiz.error_message = str(exc)
        quiz.save(update_fields=['status', 'error_message', 'updated_at'])

        # Retry logic: we use raise self.retry which respects max_retries
        try:
            # 60 seconds backoff for Celery retry
            raise self.retry(exc=exc, countdown=60)
        except self.MaxRetriesExceededError:
            logger.error(f"Max retries exceeded for Quiz {quiz_id}")
