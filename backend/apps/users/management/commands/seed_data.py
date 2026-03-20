from django.core.management.base import BaseCommand
from django.conf import settings
from apps.users.models import User
from apps.quizzes.models import Quiz, Question, Choice


class Command(BaseCommand):
    help = 'Seeds the database with an admin user and sample quizzes.'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...')

        # 1. Create Admin User
        admin_email = 'admin@quiz.com'
        if not User.objects.filter(email=admin_email).exists():
            admin_user = User.objects.create_superuser(
                email=admin_email,
                username='admin',
                password='admin123'
            )
            self.stdout.write(self.style.SUCCESS(f'Created admin user: {admin_email} / admin123'))
        else:
            admin_user = User.objects.get(email=admin_email)
            self.stdout.write(f'Admin user {admin_email} already exists.')

        # 1.5 Create Normal User
        user_email = 'user@quiz.com'
        if not User.objects.filter(email=user_email).exists():
            normal_user = User.objects.create_user(
                email=user_email,
                username='student',
                password='User@123'
            )
            # Make sure role is student implicitly
            self.stdout.write(self.style.SUCCESS(f'Created normal user: {user_email} / User@123'))
        else:
            self.stdout.write(f'Normal user {user_email} already exists.')

        # 2. Create Sample Quiz
        if not Quiz.objects.filter(title='Sample Python Quiz').exists():
            quiz = Quiz.objects.create(
                created_by=admin_user,
                title='Sample Python Quiz',
                topic='Python Programming Basics',
                difficulty='easy',
                question_count=2,
                time_limit_minutes=5,
                is_public=True,
                status='ready'
            )

            # Question 1
            q1 = Question.objects.create(
                quiz=quiz,
                order=1,
                question_text='What is the output of print(2 ** 3)?',
                question_type='mcq',
                explanation='The ** operator is used for exponentiation. 2 to the power of 3 is 8.',
                points=1
            )
            Choice.objects.create(question=q1, choice_text='6', is_correct=False, order=1)
            Choice.objects.create(question=q1, choice_text='8', is_correct=True, order=2)
            Choice.objects.create(question=q1, choice_text='9', is_correct=False, order=3)
            Choice.objects.create(question=q1, choice_text='12', is_correct=False, order=4)

            # Question 2
            q2 = Question.objects.create(
                quiz=quiz,
                order=2,
                question_text='Python is an interpreted language.',
                question_type='true_false',
                explanation='Python code is interpreted by the Python interpreter at runtime.',
                points=1
            )
            Choice.objects.create(question=q2, choice_text='True', is_correct=True, order=1)
            Choice.objects.create(question=q2, choice_text='False', is_correct=False, order=2)

            self.stdout.write(self.style.SUCCESS(f'Created sample quiz: {quiz.title}'))
        else:
            self.stdout.write('Sample quiz already exists.')

        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully.'))
