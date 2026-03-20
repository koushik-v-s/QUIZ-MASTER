"""
Tests for the Analytics app — stat refresh, topic performance, and API endpoints.
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.users.models import User
from apps.quizzes.models import Quiz, Question, Choice
from apps.attempts.models import Attempt, AttemptAnswer
from apps.analytics.models import UserStat, TopicPerformance, QuizStat


class UserStatTest(TestCase):
    """Tests for UserStat refresh logic."""

    def setUp(self):
        self.admin = User.objects.create_superuser(
            email='admin@test.com', username='testadmin', password='admin123'
        )
        self.user = User.objects.create_user(
            email='user@test.com', username='testuser', password='user123'
        )
        self.quiz = Quiz.objects.create(
            created_by=self.admin, title='Analytics Quiz', topic='Python',
            difficulty='easy', question_count=1, status='ready', time_limit_minutes=5
        )
        self.q = Question.objects.create(
            quiz=self.quiz, order=1, question_text='AQ?', explanation='E', points=1
        )
        self.c_correct = Choice.objects.create(question=self.q, choice_text='R', is_correct=True, order=1)
        self.c_wrong = Choice.objects.create(question=self.q, choice_text='W', is_correct=False, order=2)
        Choice.objects.create(question=self.q, choice_text='W2', is_correct=False, order=3)
        Choice.objects.create(question=self.q, choice_text='W3', is_correct=False, order=4)

    def test_refresh_creates_stat(self):
        """UserStat.refresh_for_user should create a UserStat if none exists."""
        self.assertFalse(UserStat.objects.filter(user=self.user).exists())
        UserStat.refresh_for_user(self.user)
        self.assertTrue(UserStat.objects.filter(user=self.user).exists())

    def test_refresh_updates_after_completion(self):
        """UserStat should reflect correct counts after an attempt is completed."""
        attempt = Attempt.objects.create(user=self.user, quiz=self.quiz)
        AttemptAnswer.objects.create(
            attempt=attempt, question=self.q, selected_choice=self.c_correct, is_correct=True
        )
        attempt.complete()

        stat = UserStat.objects.get(user=self.user)
        self.assertEqual(stat.total_quizzes_taken, 1)
        self.assertEqual(stat.average_score, 100.0)
        self.assertEqual(stat.best_score, 100.0)

    def test_quiz_stat_updates_after_completion(self):
        """QuizStat should be created/updated after attempt completion."""
        attempt = Attempt.objects.create(user=self.user, quiz=self.quiz)
        AttemptAnswer.objects.create(
            attempt=attempt, question=self.q, selected_choice=self.c_wrong, is_correct=False
        )
        attempt.complete()

        quiz_stat = QuizStat.objects.get(quiz=self.quiz)
        self.assertEqual(quiz_stat.total_attempts, 1)
        self.assertEqual(quiz_stat.average_score, 0.0)

    def test_topic_performance_created(self):
        """TopicPerformance should be created after completing a quiz."""
        attempt = Attempt.objects.create(user=self.user, quiz=self.quiz)
        AttemptAnswer.objects.create(
            attempt=attempt, question=self.q, selected_choice=self.c_correct, is_correct=True
        )
        attempt.complete()

        tp = TopicPerformance.objects.filter(user=self.user, topic='Python')
        self.assertTrue(tp.exists())
        self.assertEqual(tp.first().average_score, 100.0)


class AnalyticsAPITest(TestCase):
    """Tests for Analytics API endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='user@test.com', username='testuser', password='user123'
        )

    def test_me_endpoint(self):
        """GET /analytics/me/ should return user stats."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/analytics/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_history_endpoint(self):
        """GET /analytics/history/ should return score history."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/analytics/history/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_leaderboard_endpoint(self):
        """GET /analytics/leaderboard/ should return top performers."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/analytics/leaderboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_analytics_unauthenticated(self):
        """GET /analytics/me/ without auth should return 401."""
        response = self.client.get('/api/v1/analytics/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
