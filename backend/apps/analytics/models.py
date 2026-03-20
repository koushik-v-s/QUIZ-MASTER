"""
Analytics models tracking user performance.
Denormalized for read performance on the frontend.
"""
import uuid
from django.conf import settings
from django.db import models
from django.db.models import Avg, Max, Min, Sum, Count


class UserStat(models.Model):
    """Overall aggregated stats for a user."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='stats'
    )
    total_quizzes_taken = models.PositiveIntegerField(default=0)
    total_quizzes_created = models.PositiveIntegerField(default=0)
    average_score = models.FloatField(default=0.0)
    best_score = models.FloatField(default=0.0)
    total_time_spent_seconds = models.PositiveIntegerField(default=0)
    strongest_topic = models.CharField(max_length=255, blank=True, null=True)
    weakest_topic = models.CharField(max_length=255, blank=True, null=True)
    streak_days = models.PositiveIntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'analytics_userstat'

    def __str__(self):
        return f'Stats for {self.user.username}'

    @classmethod
    def refresh_for_user(cls, user):
        """
        Recalculate all stats for a specific user based on their Attempts and Quizzes.
        Called when an attempt is completed.
        """
        stat, created = cls.objects.get_or_create(user=user)

        from apps.attempts.models import Attempt
        from apps.quizzes.models import Quiz

        # Total created
        stat.total_quizzes_created = Quiz.objects.filter(created_by=user).count()

        # Attempts data
        completed_attempts = Attempt.objects.filter(
            user=user,
            status=Attempt.Status.COMPLETED
        )
        stat.total_quizzes_taken = completed_attempts.count()

        if stat.total_quizzes_taken > 0:
            aggs = completed_attempts.aggregate(
                avg_score=Avg('score'),
                max_score=Max('score'),
                total_time=Sum('time_taken_seconds')
            )
            stat.average_score = round(aggs['avg_score'] or 0.0, 2)
            stat.best_score = aggs['max_score'] or 0.0
            stat.total_time_spent_seconds = aggs['total_time'] or 0

            # Update TopicPerformance records
            TopicPerformance.refresh_topics_for_user(user, completed_attempts)

            # Determine strongest/weakest topics
            topics = TopicPerformance.objects.filter(user=user, attempts_count__gt=0).order_by('-average_score')
            if topics.exists():
                strongest = topics.first()
                if strongest.average_score > 50:
                    stat.strongest_topic = strongest.topic
                else:
                    stat.strongest_topic = "Keep discovering your strengths!"
                
                weakest = topics.last()
                if weakest.average_score <= 50:
                    stat.weakest_topic = weakest.topic
                else:
                    stat.weakest_topic = "Great work! No weak topics found."
            else:
                stat.strongest_topic = "Take quizzes to find your strengths!"
                stat.weakest_topic = "Take quizzes to find your weaknesses!"

            # Update streak
            if completed_attempts.exists():
                latest_date = completed_attempts.latest('completed_at').completed_at.date()
                if not stat.last_activity_date:
                    stat.streak_days = 1
                    stat.last_activity_date = latest_date
                else:
                    delta = (latest_date - stat.last_activity_date).days
                    if delta == 1:
                        stat.streak_days += 1
                        stat.last_activity_date = latest_date
                    elif delta > 1:
                        stat.streak_days = 1
                        stat.last_activity_date = latest_date
        else:
            stat.average_score = 0.0
            stat.best_score = 0.0
            stat.total_time_spent_seconds = 0
            stat.strongest_topic = None
            stat.weakest_topic = None

        stat.save()
        return stat


class TopicPerformance(models.Model):
    """User performance breakdown per topic."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='topic_performances'
    )
    topic = models.CharField(max_length=255)
    attempts_count = models.PositiveIntegerField(default=0)
    average_score = models.FloatField(default=0.0)
    best_score = models.FloatField(default=0.0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'analytics_topicperformance'
        unique_together = ('user', 'topic')
        indexes = [
            models.Index(fields=['user', 'topic']),
        ]

    def __str__(self):
        return f'{self.user.username} - {self.topic}'

    @classmethod
    def refresh_topics_for_user(cls, user, completed_attempts):
        """Update TopicPerformance records based on recent attempts."""
        topics = completed_attempts.values_list('quiz__topic', flat=True).distinct()

        for topic in topics:
            topic_attempts = completed_attempts.filter(quiz__topic=topic)
            aggs = topic_attempts.aggregate(
                avg_score=Avg('score'),
                max_score=Max('score')
            )

            cls.objects.update_or_create(
                user=user,
                topic=topic,
                defaults={
                    'attempts_count': topic_attempts.count(),
                    'average_score': round(aggs['avg_score'] or 0.0, 2),
                    'best_score': aggs['max_score'] or 0.0,
                }
            )


class QuizStat(models.Model):
    """
    Quiz-level stats for admins (denormalized for performance).
    Refreshed after every attempt completion.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.OneToOneField(
        'quizzes.Quiz',
        on_delete=models.CASCADE,
        related_name='stats'
    )
    total_attempts = models.PositiveIntegerField(default=0)
    average_score = models.FloatField(default=0.0)
    highest_score = models.FloatField(default=0.0)
    lowest_score = models.FloatField(default=0.0)
    completion_rate = models.FloatField(default=0.0)  # % who completed vs abandoned
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'analytics_quizstat'

    def __str__(self):
        return f'Stats for quiz: {self.quiz.title}'

    @classmethod
    def refresh_for_quiz(cls, quiz):
        """
        Recalculate quiz-level stats based on all attempts for this quiz.
        Called when an attempt is completed.
        """
        stat, _ = cls.objects.get_or_create(quiz=quiz)

        from apps.attempts.models import Attempt

        all_attempts = Attempt.objects.filter(quiz=quiz).exclude(
            status=Attempt.Status.IN_PROGRESS
        )
        completed = all_attempts.filter(status=Attempt.Status.COMPLETED)

        stat.total_attempts = all_attempts.count()

        if completed.exists():
            aggs = completed.aggregate(
                avg_score=Avg('score'),
                max_score=Max('score'),
                min_score=Min('score'),
            )
            stat.average_score = round(aggs['avg_score'] or 0.0, 2)
            stat.highest_score = aggs['max_score'] or 0.0
            stat.lowest_score = aggs['min_score'] or 0.0

            if stat.total_attempts > 0:
                stat.completion_rate = round(
                    (completed.count() / stat.total_attempts) * 100, 2
                )
        else:
            stat.average_score = 0.0
            stat.highest_score = 0.0
            stat.lowest_score = 0.0
            stat.completion_rate = 0.0

        stat.save()
        return stat
