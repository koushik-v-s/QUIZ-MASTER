"""
Tests for the Users app — model creation and authentication endpoints.
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.users.models import User


class UserModelTest(TestCase):
    """Tests for the custom User model."""

    def test_create_user(self):
        """Regular user creation should set role='user' and is_staff=False."""
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='securepassword123'
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.role, 'user')
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_active)
        self.assertTrue(user.check_password('securepassword123'))

    def test_create_superuser(self):
        """Superuser creation should set role='admin' and is_staff=True."""
        admin = User.objects.create_superuser(
            email='admin@example.com',
            username='adminuser',
            password='adminpass123'
        )
        self.assertEqual(admin.role, 'admin')
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_user_str(self):
        """User __str__ should return 'username (email)'."""
        user = User.objects.create_user(
            email='display@test.com', username='displayuser', password='pass123'
        )
        self.assertEqual(str(user), 'displayuser (display@test.com)')

    def test_email_required(self):
        """Creating a user without email should raise ValueError."""
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', username='noemail', password='pass123')

    def test_username_required(self):
        """Creating a user without username should raise ValueError."""
        with self.assertRaises(ValueError):
            User.objects.create_user(email='noname@test.com', username='', password='pass123')

    def test_email_uniqueness(self):
        """Duplicate emails should raise an IntegrityError."""
        User.objects.create_user(email='dup@test.com', username='user1', password='pass123')
        with self.assertRaises(Exception):
            User.objects.create_user(email='dup@test.com', username='user2', password='pass123')


class AuthEndpointTest(TestCase):
    """Tests for authentication API endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/v1/auth/register/'
        self.login_url = '/api/v1/auth/login/'
        self.me_url = '/api/v1/auth/me/'

    def test_register_user(self):
        """POST /auth/register/ should create a new user and return tokens."""
        response = self.client.post(self.register_url, {
            'email': 'new@example.com',
            'username': 'newuser',
            'password': 'strongPass123',
            'password_confirm': 'strongPass123',
        }, format='json')
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_200_OK])

    def test_login_user(self):
        """POST /auth/login/ with valid credentials should return JWT tokens."""
        User.objects.create_user(
            email='login@test.com', username='loginuser', password='testpass123'
        )
        response = self.client.post(self.login_url, {
            'email': 'login@test.com',
            'password': 'testpass123',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_wrong_password(self):
        """POST /auth/login/ with wrong password should return 401."""
        User.objects.create_user(
            email='wrong@test.com', username='wronguser', password='correctpass'
        )
        response = self.client.post(self.login_url, {
            'email': 'wrong@test.com',
            'password': 'wrongpass',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_unauthenticated(self):
        """GET /auth/me/ without token should return 401."""
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_authenticated(self):
        """GET /auth/me/ with valid token should return user profile."""
        user = User.objects.create_user(
            email='me@test.com', username='meuser', password='testpass123'
        )
        self.client.force_authenticate(user=user)
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
