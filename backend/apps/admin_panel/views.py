import logging
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import serializers as drf_serializers
from drf_spectacular.utils import extend_schema
from django.db.models import Avg, Count

from core.permissions import IsAdminRole, IsAuthenticatedAndVerified
from apps.users.models import User
from apps.users.serializers import UserProfileSerializer
from apps.quizzes.models import Quiz
from apps.quizzes.serializers import QuizListSerializer
from apps.attempts.models import Attempt

logger = logging.getLogger(__name__)


class AdminUserSerializer(drf_serializers.ModelSerializer):
    """Serializer for admin user management — allows role updates."""
    created_at = drf_serializers.DateTimeField(source='date_joined', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'role', 'is_active', 'avatar_url', 'created_at')
        read_only_fields = ('id', 'email', 'created_at')


class AdminUserViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Admin endpoints for viewing users."""
    
    queryset = User.objects.filter(role='user').order_by('-date_joined')
    serializer_class = AdminUserSerializer
    permission_classes = [IsAuthenticatedAndVerified, IsAdminRole]

    @extend_schema(summary="List all regular users (Admin only)")
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Users retrieved successfully.'
        })


class AdminQuizViewSet(mixins.ListModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """Admin endpoints for managing all quizzes (including private ones)."""
    
    queryset = Quiz.objects.select_related('created_by').all().order_by('-created_at')
    serializer_class = QuizListSerializer
    permission_classes = [IsAuthenticatedAndVerified, IsAdminRole]
    search_fields = ['title', 'topic', 'created_by__username']
    filterset_fields = ['status', 'difficulty', 'is_public']

    @extend_schema(summary="List all quizzes including private ones (Admin only)")
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            'success': True,
            'data': response.data,
            'message': 'Quizzes retrieved successfully.'
        })

    @extend_schema(summary="Force delete any quiz (Admin only)")
    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({
            'success': True,
            'data': None,
            'message': 'Quiz deleted successfully.'
        }, status=status.HTTP_200_OK)

    @extend_schema(summary="Get leaderboard for a specific quiz (Admin only)")
    @action(detail=True, methods=['GET'], url_path='leaderboard')
    def leaderboard(self, request, pk=None):
        """Get the leaderboard for a specific quiz — all user attempts with scores."""
        try:
            quiz = Quiz.objects.get(pk=pk)
        except Quiz.DoesNotExist:
            return Response({
                'success': False,
                'error': {'message': 'Quiz not found.'}
            }, status=status.HTTP_404_NOT_FOUND)

        # Get all completed attempts for this quiz, ordered by score desc
        attempts = Attempt.objects.filter(
            quiz=quiz,
            status=Attempt.Status.COMPLETED
        ).select_related('user').order_by('-score', 'completed_at')

        leaderboard_data = []
        for rank, attempt in enumerate(attempts, start=1):
            leaderboard_data.append({
                'rank': rank,
                'username': attempt.user.username,
                'email': attempt.user.email,
                'score': attempt.score,
                'completed_at': attempt.completed_at,
            })

        return Response({
            'success': True,
            'data': {
                'quiz_id': str(quiz.id),
                'quiz_title': quiz.title,
                'quiz_topic': quiz.topic,
                'total_attempts': len(leaderboard_data),
                'leaderboard': leaderboard_data
            },
            'message': 'Leaderboard retrieved.'
        })


class AdminLeaderboardViewSet(viewsets.ViewSet):
    """Admin endpoint to get per-quiz leaderboard for quizzes created by the admin."""
    
    permission_classes = [IsAuthenticatedAndVerified, IsAdminRole]

    @extend_schema(summary="Get leaderboards for all quizzes created by the current admin")
    def list(self, request):
        """Return all quizzes created by the admin with their leaderboards."""
        my_quizzes = Quiz.objects.filter(
            created_by=request.user,
            status=Quiz.Status.READY
        ).order_by('-created_at')

        result = []
        for quiz in my_quizzes:
            attempts = Attempt.objects.filter(
                quiz=quiz,
                status=Attempt.Status.COMPLETED
            ).select_related('user').order_by('-score', 'completed_at')

            entries = []
            for rank, attempt in enumerate(attempts, start=1):
                entries.append({
                    'rank': rank,
                    'username': attempt.user.username,
                    'email': attempt.user.email,
                    'score': attempt.score,
                    'completed_at': attempt.completed_at,
                })

            result.append({
                'quiz_id': str(quiz.id),
                'quiz_title': quiz.title,
                'quiz_topic': quiz.topic,
                'difficulty': quiz.difficulty,
                'question_count': quiz.question_count,
                'total_attempts': len(entries),
                'leaderboard': entries,
            })

        return Response({
            'success': True,
            'data': result,
            'message': 'Leaderboards retrieved.'
        })


class AdminStatsViewSet(viewsets.ViewSet):
    """Admin endpoints for platform-wide statistics."""
    
    permission_classes = [IsAuthenticatedAndVerified, IsAdminRole]

    @extend_schema(summary="Get platform-wide statistics (Admin only)")
    def list(self, request):
        total_users = User.objects.filter(role='user').count()
        total_quizzes = Quiz.objects.count()
        total_attempts = Attempt.objects.count()
        completed_attempts = Attempt.objects.filter(status=Attempt.Status.COMPLETED)
        completed_count = completed_attempts.count()
        
        # Calculate completion rate
        completion_rate = 0
        if total_attempts > 0:
            completion_rate = round((completed_count / total_attempts) * 100, 2)

        # Average score across all completed attempts
        avg_score_result = completed_attempts.aggregate(avg=Avg('score'))
        average_score = avg_score_result['avg'] or 0

        # Quiz counts by status
        status_counts = Quiz.objects.values('status').annotate(count=Count('id'))
        quizzes_by_status = {}
        for entry in status_counts:
            quizzes_by_status[entry['status']] = entry['count']

        data = {
            'total_users': total_users,
            'total_quizzes': total_quizzes,
            'total_attempts': total_attempts,
            'completed_attempts': completed_count,
            'completion_rate_percentage': completion_rate,
            'average_score': average_score,
            'quizzes_by_status': quizzes_by_status,
        }

        return Response({
            'success': True,
            'data': data,
            'message': 'Platform statistics retrieved.'
        })
