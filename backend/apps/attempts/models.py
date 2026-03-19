"""
Attempt and AttemptAnswer models for quiz attempt tracking and scoring.
"""
import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone


class Attempt(models.Model):
    """Tracks a user's attempt at a quiz."""

    class Status(models.TextChoices):
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'
        ABANDONED = 'abandoned', 'Abandoned'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='attempts'
    )
    quiz = models.ForeignKey(
        'quizzes.Quiz',
        on_delete=models.CASCADE,
        related_name='attempts'
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.IN_PROGRESS)
    score = models.FloatField(default=0.0)  # 0-100 percentage
    total_points_earned = models.PositiveIntegerField(default=0)
    total_points_possible = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_taken_seconds = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'attempts_attempt'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['user', 'quiz']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['quiz', 'status']),
        ]

    def __str__(self):
        return f'{self.user.username} → {self.quiz.title} ({self.status})'

    def calculate_score(self):
        """Calculate score from answered questions using DB aggregation."""
        answers = self.answers.all()
        total_possible = answers.count()
        total_correct = answers.filter(is_correct=True).count()

        if total_possible == 0:
            return 0.0

        # Get actual points
        from django.db.models import Sum
        points_earned = answers.filter(is_correct=True).aggregate(
            total=Sum('question__points')
        )['total'] or 0

        points_possible = answers.aggregate(
            total=Sum('question__points')
        )['total'] or 0

        self.total_points_earned = points_earned
        self.total_points_possible = points_possible

        if points_possible > 0:
            self.score = round((points_earned / points_possible) * 100, 2)
        else:
            self.score = 0.0

        return self.score

    def complete(self):
        """Complete the attempt: calculate score and set timestamps."""
        self.calculate_score()
        self.status = self.Status.COMPLETED
        self.completed_at = timezone.now()
        self.time_taken_seconds = int(
            (self.completed_at - self.started_at).total_seconds()
        )
        self.save(update_fields=[
            'status', 'score', 'total_points_earned',
            'total_points_possible', 'completed_at', 'time_taken_seconds'
        ])

        # Update analytics for the user and quiz
        from apps.analytics.models import UserStat, QuizStat
        UserStat.refresh_for_user(self.user)
        QuizStat.refresh_for_quiz(self.quiz)

        return self


class AttemptAnswer(models.Model):
    """Tracks an individual answer within an attempt."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(
        'quizzes.Question',
        on_delete=models.CASCADE,
        related_name='attempt_answers'
    )
    selected_choice = models.ForeignKey(
        'quizzes.Choice',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attempt_answers'
    )
    is_correct = models.BooleanField(default=False)
    time_taken_seconds = models.PositiveIntegerField(default=0)
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'attempts_attemptanswer'
        unique_together = ('attempt', 'question')
        ordering = ['answered_at']

    def __str__(self):
        status = '✓' if self.is_correct else '✗'
        return f'{status} {self.question.question_text[:50]}'
