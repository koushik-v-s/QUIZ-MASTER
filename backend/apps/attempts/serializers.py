"""
Serializers for attempt tracking and scoring.
"""
from rest_framework import serializers
from django.utils import timezone
from .models import Attempt, AttemptAnswer
from apps.quizzes.models import Quiz, Question, Choice
from apps.quizzes.serializers import QuestionWithAnswerSerializer


class AttemptListSerializer(serializers.ModelSerializer):
    """Serialize basic info for a list of attempts."""
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    quiz_topic = serializers.CharField(source='quiz.topic', read_only=True)

    class Meta:
        model = Attempt
        fields = (
            'id', 'quiz', 'quiz_title', 'quiz_topic', 'status',
            'score', 'started_at', 'completed_at', 'time_taken_seconds'
        )


class AttemptStartSerializer(serializers.Serializer):
    """Serializer for starting a new attempt."""
    quiz_id = serializers.UUIDField()

    def validate_quiz_id(self, value):
        try:
            quiz = Quiz.objects.get(id=value)
        except Quiz.DoesNotExist:
            raise serializers.ValidationError("Quiz does not exist.")

        if quiz.status != Quiz.Status.READY:
            raise serializers.ValidationError("This quiz is not ready yet.")
            
        # Check permissions for private quizzes
        request = self.context.get('request')
        if not quiz.is_public and request and request.user != quiz.created_by and request.user.role != 'admin':
            raise serializers.ValidationError("You don't have permission to take this quiz.")

        return value


class AttemptAnswerSubmitSerializer(serializers.Serializer):
    """Serializer for submitting an answer."""
    question_id = serializers.UUIDField()
    choice_id = serializers.UUIDField()
    time_taken_seconds = serializers.IntegerField(min_value=0, default=0)

    def validate(self, data):
        attempt = self.context.get('attempt')
        if not attempt:
            raise serializers.ValidationError("Attempt context is missing.")

        if attempt.status != Attempt.Status.IN_PROGRESS:
            raise serializers.ValidationError("Attempt is already completed or abandoned.")

        try:
            question = Question.objects.get(id=data['question_id'], quiz=attempt.quiz)
        except Question.DoesNotExist:
            raise serializers.ValidationError({"question_id": "Question not found in this quiz."})

        try:
            choice = Choice.objects.get(id=data['choice_id'], question=question)
        except Choice.DoesNotExist:
            raise serializers.ValidationError({"choice_id": "Choice does not belong to this question."})

        # Check if already answered
        if AttemptAnswer.objects.filter(attempt=attempt, question=question).exists():
            raise serializers.ValidationError("You have already answered this question.")

        data['question'] = question
        data['choice'] = choice
        return data


class AttemptResultSerializer(serializers.ModelSerializer):
    """Serialize full attempt results, including correct answers and explanations."""
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    answers = serializers.SerializerMethodField()

    class Meta:
        model = Attempt
        fields = (
            'id', 'quiz_title', 'status', 'score',
            'total_points_earned', 'total_points_possible',
            'started_at', 'completed_at', 'time_taken_seconds', 'answers'
        )

    def get_answers(self, obj):
        # Return complete breakdown of questions and answers
        # This gives the UI the exact context to show right/wrong and explanations
        results = []
        user_answers = {ans.question_id: ans for ans in obj.answers.select_related('selected_choice')}
        questions = obj.quiz.get_questions_with_choices()

        for q in questions:
            user_ans = user_answers.get(q.id)
            serialized_q = QuestionWithAnswerSerializer(q).data

            results.append({
                'question': serialized_q,
                'user_selected_choice_id': user_ans.selected_choice_id if user_ans else None,
                'is_correct': user_ans.is_correct if user_ans else False,
                'time_taken_seconds': user_ans.time_taken_seconds if user_ans else 0,
            })
        return results
