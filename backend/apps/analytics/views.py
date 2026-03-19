"""
API Views for Analytics metrics and Leaderboard.
"""
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from drf_spectacular.utils import extend_schema

from core.permissions import IsUserRole, IsAdminRole, IsQuizOwner
from .models import UserStat, TopicPerformance, QuizStat
from apps.attempts.models import Attempt
from .serializers import (
    UserStatSerializer,
    TopicPerformanceSerializer,
    LeaderboardSerializer,
    ScoreHistorySerializer,
    QuizStatSerializer
)


class AnalyticsViewSet(viewsets.GenericViewSet):
    """
    Endpoints for retrieving user analytics data.
    /me/, /me/topics/, /me/history/ → IsUserRole ONLY
    /leaderboard/ → IsAuthenticated (both roles)
    """

    def get_permissions(self):
        if self.action == 'leaderboard':
            return [IsAuthenticated()]
        # All /me/* endpoints are user-only
        return [IsAuthenticated(), IsUserRole()]

    @extend_schema(summary="Get current user overall stats", responses={200: UserStatSerializer})
    @action(detail=False, methods=['GET'])
    def me(self, request):
        """Get the current user's general statistics."""
        stat, _ = UserStat.objects.get_or_create(user=request.user)

        # Cache for 2 minutes
        cache_key = f"user_stats_{request.user.id}"
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        serializer = UserStatSerializer(stat)
        response_data = {
            'success': True,
            'data': serializer.data,
            'message': 'User stats retrieved.'
        }
        cache.set(cache_key, response_data, timeout=120)
        return Response(response_data)

    @extend_schema(summary="Get per-topic performance breakdown", responses={200: TopicPerformanceSerializer(many=True)})
    @action(detail=False, methods=['GET'])
    def topics(self, request):
        """Get performance broken down by topic for the radar chart."""
        topics = TopicPerformance.objects.filter(user=request.user).order_by('-attempts_count')
        serializer = TopicPerformanceSerializer(topics, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Topic performance retrieved.'
        })

    @extend_schema(summary="Get score history over time", responses={200: ScoreHistorySerializer(many=True)})
    @action(detail=False, methods=['GET'])
    def history(self, request):
        """Get the last 20 completed attempts with scores to plug into a line chart."""
        attempts = Attempt.objects.select_related('quiz').filter(
            user=request.user,
            status=Attempt.Status.COMPLETED
        ).order_by('-completed_at')[:20]

        data = []
        for att in reversed(attempts):
            data.append({
                'date': att.completed_at,
                'score': att.score,
                'quiz_title': att.quiz.title,
                'topic': att.quiz.topic,
            })

        serializer = ScoreHistorySerializer(data, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Score history retrieved.'
        })

    @extend_schema(summary="Get public leaderboard", responses={200: LeaderboardSerializer(many=True)})
    @action(detail=False, methods=['GET'])
    def leaderboard(self, request):
        """Get the top 50 users based on average score (requires minimum 3 quizzes taken)."""
        cache_key = "global_leaderboard"
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        top_stats = UserStat.objects.select_related('user').filter(
            total_quizzes_taken__gte=3,
            user__is_active=True
        ).order_by('-average_score', '-total_quizzes_taken')[:50]

        serializer = LeaderboardSerializer(top_stats, many=True)

        response_data = {
            'success': True,
            'data': serializer.data,
            'message': 'Leaderboard retrieved.'
        }

        cache.set(cache_key, response_data, timeout=60)
        return Response(response_data)


class QuizStatsViewSet(viewsets.GenericViewSet):
    """
    Admin-facing quiz stats endpoint.
    GET /analytics/quiz/{id}/stats/ → IsAdminRole + must own quiz
    """
    permission_classes = [IsAuthenticated, IsAdminRole]

    @extend_schema(summary="Get stats for a specific quiz (admin only)")
    @action(detail=False, methods=['GET'], url_path='(?P<quiz_id>[^/.]+)/stats')
    def quiz_stats(self, request, quiz_id=None):
        """Stats for a specific quiz — admin only, must own quiz."""
        from apps.quizzes.models import Quiz

        try:
            quiz = Quiz.objects.get(id=quiz_id)
        except Quiz.DoesNotExist:
            return Response({
                'success': False,
                'error': {'code': 'NOT_FOUND', 'message': 'Quiz not found.'}
            }, status=status.HTTP_404_NOT_FOUND)

        # Only quiz owner or superuser
        if quiz.created_by != request.user and not request.user.is_superuser:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You do not own this quiz.")

        # Cache for 3 minutes
        cache_key = f"quiz_stats_{quiz_id}"
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        stat, _ = QuizStat.objects.get_or_create(quiz=quiz)
        stat.refresh_for_quiz(quiz)

        serializer = QuizStatSerializer(stat)
        response_data = {
            'success': True,
            'data': serializer.data,
            'message': 'Quiz statistics retrieved.'
        }
        cache.set(cache_key, response_data, timeout=180)
        return Response(response_data)
