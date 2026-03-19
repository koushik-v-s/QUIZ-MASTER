"""
API views for Quiz generation, CRUD, and status polling.
"""
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.cache import cache
from django.utils.timezone import now
from django.db.models import Avg, Count, Max, Min
from datetime import date
from drf_spectacular.utils import extend_schema

from core.permissions import IsAdminRole, IsQuizOwner
from core.exceptions import QuotaExceeded
from .models import Quiz
from .serializers import (
    QuizListSerializer,
    QuizDetailSerializer,
    QuizCreateSerializer
)
from .tasks import generate_quiz_questions
from django.conf import settings


def check_ai_rate_limit(user):
    """Check and increment daily AI generation limit via cache."""
    key = f"ai_gen_count:{user.id}:{date.today()}"
    limit = getattr(settings, 'AI_GENERATION_RATE_LIMIT', 10)

    count = cache.get(key, 0)
    if count >= limit:
        raise QuotaExceeded(f"Daily AI generation limit ({limit}) reached. Try again tomorrow.")

    if count == 0:
        cache.set(key, 1, timeout=86400)  # 24 hours
    else:
        cache.incr(key)


def check_duplicate_generation(user, topic, difficulty):
    """Prevent duplicate in-flight generations."""
    exists = Quiz.objects.filter(
        created_by=user, topic=topic, difficulty=difficulty, status='generating'
    ).exists()
    if exists:
        from rest_framework.exceptions import ValidationError
        raise ValidationError("A quiz with this topic and difficulty is already being generated.")


class QuizViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Quizzes: list public quizzes, create/generate, update, delete.
    """

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        if self.action in ['my', 'status', 'regenerate', 'create', 'attempt_stats']:
            return [IsAuthenticated(), IsAdminRole()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminRole(), IsQuizOwner()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return QuizCreateSerializer
        if self.action == 'retrieve':
            return QuizDetailSerializer
        return QuizListSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Quiz.objects.select_related('created_by')

        if self.action == 'list':
            # Users see only public+ready quizzes; admins see all their own
            if user.role == 'admin':
                return qs.filter(created_by=user)
            return qs.filter(is_public=True, status=Quiz.Status.READY)

        return qs

    @extend_schema(summary="List all public quizzes")
    def list(self, request, *args, **kwargs):
        cache_key = f"quiz_list_{request.user.role}_{request.query_params.urlencode()}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)

        formatted_response = {
            'success': True,
            'data': response.data,
            'message': 'Quizzes retrieved successfully'
        }

        cache.set(cache_key, formatted_response, timeout=300)
        return Response(formatted_response)

    @extend_schema(summary="Create a quiz and trigger AI generation")
    def create(self, request, *args, **kwargs):
        # Rate limit check
        check_ai_rate_limit(request.user)

        # Duplicate generation check
        check_duplicate_generation(
            request.user,
            request.data.get('topic', ''),
            request.data.get('difficulty', 'medium')
        )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        quiz = serializer.save()

        # Trigger Celery task
        from django.db import transaction
        transaction.on_commit(lambda: generate_quiz_questions.delay(str(quiz.id)))

        # Calculate remaining generations today
        key = f"ai_gen_count:{request.user.id}:{date.today()}"
        count = cache.get(key, 0)
        limit = getattr(settings, 'AI_GENERATION_RATE_LIMIT', 10)

        detail_serializer = QuizDetailSerializer(quiz)
        return Response({
            'success': True,
            'data': detail_serializer.data,
            'message': 'Quiz created. AI generation started.',
            'meta': {
                'generations_remaining_today': limit - count,
            }
        }, status=status.HTTP_201_CREATED)

    @extend_schema(summary="Retrieve quiz details (with questions if ready)")
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        if not instance.is_public and (
            not request.user.is_authenticated
            or (request.user != instance.created_by and request.user.role != 'admin')
        ):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("This quiz is private.")

        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Quiz retrieved successfully'
        })

    @extend_schema(summary="Update quiz settings")
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({
            'success': True,
            'data': response.data,
            'message': 'Quiz updated successfully'
        })

    @extend_schema(summary="Delete a quiz")
    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({
            'success': True,
            'data': None,
            'message': 'Quiz deleted successfully'
        })

    @extend_schema(summary="List current admin's quizzes")
    @action(detail=False, methods=['GET'])
    def my(self, request):
        qs = Quiz.objects.select_related('created_by').filter(created_by=request.user)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = QuizListSerializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            return Response({
                'success': True,
                'data': response.data,
                'message': 'Your quizzes retrieved'
            })

        serializer = QuizListSerializer(qs, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Your quizzes retrieved'
        })

    @extend_schema(summary="Poll generation status")
    @action(detail=True, methods=['GET'])
    def status(self, request, pk=None):
        quiz = self.get_object()
        return Response({
            'success': True,
            'data': {
                'id': quiz.id,
                'status': quiz.status,
                'error_message': quiz.error_message
            },
            'message': 'Quiz status retrieved'
        })

    @extend_schema(summary="Re-trigger AI generation")
    @action(detail=True, methods=['POST'])
    def regenerate(self, request, pk=None):
        quiz = self.get_object()

        check_ai_rate_limit(request.user)

        # Clear old questions
        quiz.questions.all().delete()
        quiz.status = Quiz.Status.GENERATING
        quiz.error_message = ""
        quiz.save(update_fields=['status', 'error_message'])

        generate_quiz_questions.delay(str(quiz.id))

        return Response({
            'success': True,
            'data': {'id': quiz.id, 'status': quiz.status},
            'message': 'AI regeneration started.'
        })

    @extend_schema(summary="Get attempt statistics for a quiz")
    @action(detail=True, methods=['GET'], url_path='attempt-stats')
    def attempt_stats(self, request, pk=None):
        """Attempt count, avg score, top scorers for a specific quiz (admin only)."""
        quiz = self.get_object()

        # Only quiz owner can see stats
        if quiz.created_by != request.user and not request.user.is_superuser:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You do not own this quiz.")

        from apps.attempts.models import Attempt
        completed = Attempt.objects.filter(quiz=quiz, status=Attempt.Status.COMPLETED)

        stats = completed.aggregate(
            total_attempts=Count('id'),
            avg_score=Avg('score'),
            highest_score=Max('score'),
            lowest_score=Min('score'),
        )

        # Top 10 scorers
        top_scorers = completed.select_related('user').order_by('-score')[:10]
        top_scorers_data = [
            {
                'username': a.user.username,
                'score': a.score,
                'time_taken_seconds': a.time_taken_seconds,
                'completed_at': a.completed_at,
            }
            for a in top_scorers
        ]

        return Response({
            'success': True,
            'data': {
                'quiz_id': quiz.id,
                'quiz_title': quiz.title,
                'total_attempts': stats['total_attempts'] or 0,
                'average_score': round(stats['avg_score'] or 0, 2),
                'highest_score': stats['highest_score'] or 0,
                'lowest_score': stats['lowest_score'] or 0,
                'top_scorers': top_scorers_data,
            },
            'message': 'Quiz attempt stats retrieved.'
        })
