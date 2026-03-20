"""
Tests for the Quizzes app — model logic, API endpoints, and AI generation flow.
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.users.models import User
from apps.quizzes.models import Quiz, Question, Choice


class QuizModelTest(TestCase):
    """Tests for Quiz, Question, and Choice models."""

    def setUp(self):
        self.admin = User.objects.create_superuser(
            email='admin@test.com', username='testadmin', password='admin123'
        )

    def test_create_quiz(self):
        """Quiz creation should set default status to 'generating'."""
        quiz = Quiz.objects.create(
            created_by=self.admin,
            title='Test Quiz',
            topic='Python',
            difficulty='easy',
            question_count=5,
            time_limit_minutes=10
        )
        self.assertEqual(quiz.status, 'generating')
        self.assertEqual(quiz.topic, 'Python')
        self.assertEqual(quiz.question_count, 5)

    def test_quiz_str(self):
        """Quiz __str__ should return 'title (topic - difficulty)'."""
        quiz = Quiz.objects.create(
            created_by=self.admin, title='My Quiz', topic='Django', difficulty='hard', question_count=3
        )
        self.assertIn('My Quiz', str(quiz))
        self.assertIn('Django', str(quiz))

    def test_quiz_queryset_public(self):
        """QuizManager.public() should only return public quizzes."""
        Quiz.objects.create(created_by=self.admin, title='Public', topic='A', is_public=True, question_count=1)
        Quiz.objects.create(created_by=self.admin, title='Private', topic='B', is_public=False, question_count=1)
        self.assertEqual(Quiz.objects.public().count(), 1)

    def test_quiz_queryset_ready(self):
        """QuizManager.ready() should only return quizzes with status='ready'."""
        Quiz.objects.create(created_by=self.admin, title='Ready', topic='A', status='ready', question_count=1)
        Quiz.objects.create(created_by=self.admin, title='Generating', topic='B', status='generating', question_count=1)
        self.assertEqual(Quiz.objects.ready().count(), 1)

    def test_create_question_with_choices(self):
        """Questions and Choices should be linked correctly."""
        quiz = Quiz.objects.create(
            created_by=self.admin, title='Q Quiz', topic='Test', question_count=1
        )
        question = Question.objects.create(
            quiz=quiz, order=1, question_text='What is 2+2?',
            explanation='Basic math.', points=1
        )
        Choice.objects.create(question=question, choice_text='3', is_correct=False, order=1)
        Choice.objects.create(question=question, choice_text='4', is_correct=True, order=2)
        Choice.objects.create(question=question, choice_text='5', is_correct=False, order=3)
        Choice.objects.create(question=question, choice_text='6', is_correct=False, order=4)

        self.assertEqual(question.choices.count(), 4)
        self.assertEqual(question.choices.filter(is_correct=True).count(), 1)


class QuizAPITest(TestCase):
    """Tests for Quiz API endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            email='admin@test.com', username='testadmin', password='admin123'
        )
        self.user = User.objects.create_user(
            email='user@test.com', username='testuser', password='user123'
        )
        self.quiz = Quiz.objects.create(
            created_by=self.admin, title='API Quiz', topic='Testing',
            difficulty='medium', question_count=5, status='ready', is_public=True
        )

    def test_list_quizzes_authenticated(self):
        """GET /quizzes/ should return a list of quizzes for authenticated users."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/quizzes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_quizzes_unauthenticated(self):
        """GET /quizzes/ without auth should return 401."""
        response = self.client.get('/api/v1/quizzes/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_quiz_detail(self):
        """GET /quizzes/:id/ should return quiz details."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/v1/quizzes/{self.quiz.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_quiz_as_admin(self):
        """DELETE /quizzes/:id/ as admin/owner should succeed."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f'/api/v1/quizzes/{self.quiz.id}/')
        self.assertIn(response.status_code, [status.HTTP_204_NO_CONTENT, status.HTTP_200_OK])

    def test_delete_quiz_as_non_owner(self):
        """DELETE /quizzes/:id/ as non-owner should be forbidden."""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'/api/v1/quizzes/{self.quiz.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_quiz_status(self):
        """GET /quizzes/:id/status/ should return current generation status."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/v1/quizzes/{self.quiz.id}/status/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
