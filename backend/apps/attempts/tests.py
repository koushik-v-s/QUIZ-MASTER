"""
Tests for the Attempts app — attempt creation, answer submission, and completion.
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.users.models import User
from apps.quizzes.models import Quiz, Question, Choice
from apps.attempts.models import Attempt, AttemptAnswer


class AttemptModelTest(TestCase):
    """Tests for Attempt and AttemptAnswer models."""

    def setUp(self):
        self.admin = User.objects.create_superuser(
            email='admin@test.com', username='testadmin', password='admin123'
        )
        self.user = User.objects.create_user(
            email='user@test.com', username='testuser', password='user123'
        )
        self.quiz = Quiz.objects.create(
            created_by=self.admin, title='Attempt Quiz', topic='Test',
            difficulty='easy', question_count=2, status='ready', time_limit_minutes=5
        )
        self.q1 = Question.objects.create(
            quiz=self.quiz, order=1, question_text='Q1?', explanation='E1', points=1
        )
        self.c1_correct = Choice.objects.create(question=self.q1, choice_text='Right', is_correct=True, order=1)
        self.c1_wrong = Choice.objects.create(question=self.q1, choice_text='Wrong', is_correct=False, order=2)
        Choice.objects.create(question=self.q1, choice_text='Wrong2', is_correct=False, order=3)
        Choice.objects.create(question=self.q1, choice_text='Wrong3', is_correct=False, order=4)

        self.q2 = Question.objects.create(
            quiz=self.quiz, order=2, question_text='Q2?', explanation='E2', points=1
        )
        self.c2_correct = Choice.objects.create(question=self.q2, choice_text='Right', is_correct=True, order=1)
        self.c2_wrong = Choice.objects.create(question=self.q2, choice_text='Wrong', is_correct=False, order=2)
        Choice.objects.create(question=self.q2, choice_text='Wrong2', is_correct=False, order=3)
        Choice.objects.create(question=self.q2, choice_text='Wrong3', is_correct=False, order=4)

    def test_create_attempt(self):
        """Creating an attempt should default to 'in_progress'."""
        attempt = Attempt.objects.create(user=self.user, quiz=self.quiz)
        self.assertEqual(attempt.status, 'in_progress')
        self.assertEqual(attempt.score, 0.0)

    def test_attempt_score_calculation_perfect(self):
        """Answering all correctly should yield 100% score."""
        attempt = Attempt.objects.create(user=self.user, quiz=self.quiz)
        AttemptAnswer.objects.create(
            attempt=attempt, question=self.q1, selected_choice=self.c1_correct, is_correct=True
        )
        AttemptAnswer.objects.create(
            attempt=attempt, question=self.q2, selected_choice=self.c2_correct, is_correct=True
        )
        attempt.complete()
        self.assertEqual(attempt.score, 100.0)
        self.assertEqual(attempt.status, 'completed')

    def test_attempt_score_calculation_partial(self):
        """Answering 1 of 2 correctly should yield 50% score."""
        attempt = Attempt.objects.create(user=self.user, quiz=self.quiz)
        AttemptAnswer.objects.create(
            attempt=attempt, question=self.q1, selected_choice=self.c1_correct, is_correct=True
        )
        AttemptAnswer.objects.create(
            attempt=attempt, question=self.q2, selected_choice=self.c2_wrong, is_correct=False
        )
        attempt.complete()
        self.assertEqual(attempt.score, 50.0)

    def test_attempt_score_calculation_zero(self):
        """Answering all incorrectly should yield 0% score."""
        attempt = Attempt.objects.create(user=self.user, quiz=self.quiz)
        AttemptAnswer.objects.create(
            attempt=attempt, question=self.q1, selected_choice=self.c1_wrong, is_correct=False
        )
        AttemptAnswer.objects.create(
            attempt=attempt, question=self.q2, selected_choice=self.c2_wrong, is_correct=False
        )
        attempt.complete()
        self.assertEqual(attempt.score, 0.0)

    def test_attempt_completion_sets_timestamp(self):
        """Completing an attempt should set completed_at."""
        attempt = Attempt.objects.create(user=self.user, quiz=self.quiz)
        self.assertIsNone(attempt.completed_at)
        attempt.complete()
        attempt.refresh_from_db()
        self.assertIsNotNone(attempt.completed_at)


class AttemptAPITest(TestCase):
    """Tests for Attempt API endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            email='admin@test.com', username='testadmin', password='admin123'
        )
        self.user = User.objects.create_user(
            email='user@test.com', username='testuser', password='user123'
        )
        self.quiz = Quiz.objects.create(
            created_by=self.admin, title='API Attempt Quiz', topic='Test',
            difficulty='easy', question_count=1, status='ready', time_limit_minutes=5
        )
        self.q = Question.objects.create(
            quiz=self.quiz, order=1, question_text='API Q?', explanation='E', points=1
        )
        self.c_correct = Choice.objects.create(question=self.q, choice_text='Right', is_correct=True, order=1)
        Choice.objects.create(question=self.q, choice_text='W1', is_correct=False, order=2)
        Choice.objects.create(question=self.q, choice_text='W2', is_correct=False, order=3)
        Choice.objects.create(question=self.q, choice_text='W3', is_correct=False, order=4)

    def test_create_attempt(self):
        """POST /attempts/ should create a new attempt."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/v1/attempts/', {'quiz_id': str(self.quiz.id)}, format='json')
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_200_OK])

    def test_list_attempts(self):
        """GET /attempts/ should return user's attempts."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/attempts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_attempts_unauthenticated(self):
        """GET /attempts/ without auth should return 401."""
        response = self.client.get('/api/v1/attempts/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
