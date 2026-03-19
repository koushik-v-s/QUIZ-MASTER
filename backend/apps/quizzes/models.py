"""
Quiz, Question, and Choice models with custom QuerySet for filtering.
"""
import uuid
from django.conf import settings
from django.db import models


class QuizQuerySet(models.QuerySet):
    """Custom QuerySet for Quiz model."""

    def public(self):
        return self.filter(is_public=True)

    def ready(self):
        return self.filter(status='ready')

    def by_user(self, user):
        return self.filter(created_by=user)

    def generating(self):
        return self.filter(status='generating')


class QuizManager(models.Manager):
    """Custom Manager using QuizQuerySet."""

    def get_queryset(self):
        return QuizQuerySet(self.model, using=self._db)

    def public(self):
        return self.get_queryset().public()

    def ready(self):
        return self.get_queryset().ready()

    def by_user(self, user):
        return self.get_queryset().by_user(user)


class Quiz(models.Model):
    """Quiz model — AI-generated quiz with topic, difficulty, and status tracking."""

    class Difficulty(models.TextChoices):
        EASY = 'easy', 'Easy'
        MEDIUM = 'medium', 'Medium'
        HARD = 'hard', 'Hard'

    class Status(models.TextChoices):
        GENERATING = 'generating', 'Generating'
        READY = 'ready', 'Ready'
        FAILED = 'failed', 'Failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quizzes'
    )
    title = models.CharField(max_length=255)
    topic = models.CharField(max_length=255)
    difficulty = models.CharField(max_length=10, choices=Difficulty.choices, default=Difficulty.MEDIUM)
    question_count = models.PositiveIntegerField(default=5)
    time_limit_minutes = models.PositiveIntegerField(null=True, blank=True)
    is_public = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.GENERATING)
    generation_prompt = models.TextField(blank=True, default='')
    ai_model_used = models.CharField(max_length=100, blank=True, default='')
    error_message = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = QuizManager()

    class Meta:
        db_table = 'quizzes_quiz'
        ordering = ['-created_at']
        verbose_name_plural = 'Quizzes'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['is_public']),
            models.Index(fields=['topic']),
            models.Index(fields=['created_by', 'created_at']),
        ]

    def __str__(self):
        return f'{self.title} ({self.topic} - {self.difficulty})'

    def get_questions_with_choices(self):
        """Get all questions with prefetched choices."""
        return self.questions.prefetch_related('choices').order_by('order')


class Question(models.Model):
    """Question model — belongs to a Quiz."""

    class QuestionType(models.TextChoices):
        MCQ = 'mcq', 'Multiple Choice'
        TRUE_FALSE = 'true_false', 'True/False'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    order = models.PositiveIntegerField(default=0)
    question_text = models.TextField()
    question_type = models.CharField(
        max_length=20,
        choices=QuestionType.choices,
        default=QuestionType.MCQ
    )
    explanation = models.TextField(blank=True, default='')
    points = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'quizzes_question'
        ordering = ['order']
        indexes = [
            models.Index(fields=['quiz', 'order']),
        ]

    def __str__(self):
        return f'Q{self.order}: {self.question_text[:80]}'


class Choice(models.Model):
    """Choice model — belongs to a Question."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'quizzes_choice'
        ordering = ['order']

    def __str__(self):
        marker = '✓' if self.is_correct else '✗'
        return f'{marker} {self.choice_text[:60]}'
