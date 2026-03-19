"""
API views for managing Quiz Attempts.
ALL endpoints → IsUserRole ONLY. Admin calling any of these gets 403.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema

from core.permissions import IsUserRole, IsAttemptOwner
from .models import Attempt, AttemptAnswer
from .serializers import (
    AttemptListSerializer,
    AttemptStartSerializer,
    AttemptAnswerSubmitSerializer,
    AttemptResultSerializer
)


class AttemptViewSet(viewsets.GenericViewSet):
    """
    ViewSet for tracking Quiz Attempts.
    All endpoints are IsUserRole ONLY — admins get 403.
    """

    permission_classes = [IsAuthenticated, IsUserRole]

    def get_queryset(self):
        return Attempt.objects.select_related(
            'quiz', 'user'
        ).prefetch_related('answers').filter(user=self.request.user)

    @extend_schema(summary="List current user's attempt history", responses={200: AttemptListSerializer(many=True)})
    def list(self, request):
        """List all attempts for the current user."""
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = AttemptListSerializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            return Response({
                'success': True,
                'data': response.data,
                'message': 'Attempt history retrieved.'
            })

        serializer = AttemptListSerializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Attempt history retrieved.'
        })

    @extend_schema(summary="Start a new quiz attempt", request=AttemptStartSerializer, responses={201: AttemptListSerializer})
    def create(self, request):
        """Start a new attempt at a quiz."""
        serializer = AttemptStartSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        quiz_id = serializer.validated_data['quiz_id']

        # Check if there is an existing in-progress attempt for this quiz (idempotency)
        existing = Attempt.objects.filter(
            user=request.user,
            quiz_id=quiz_id,
            status=Attempt.Status.IN_PROGRESS
        ).first()

        if existing:
            response_serializer = AttemptListSerializer(existing)
            return Response({
                'success': True,
                'data': response_serializer.data,
                'message': 'Resumed existing attempt.'
            }, status=status.HTTP_200_OK)

        # Prevent retake: if user has already completed this quiz, block it
        already_completed = Attempt.objects.filter(
            user=request.user,
            quiz_id=quiz_id,
            status=Attempt.Status.COMPLETED
        ).exists()

        if already_completed:
            return Response({
                'success': False,
                'error': {
                    'code': 'ALREADY_COMPLETED',
                    'message': 'You have already completed this quiz. Retakes are not allowed.'
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create new attempt
        attempt = Attempt.objects.create(
            user=request.user,
            quiz_id=quiz_id,
            status=Attempt.Status.IN_PROGRESS
        )

        response_serializer = AttemptListSerializer(attempt)
        return Response({
            'success': True,
            'data': response_serializer.data,
            'message': 'Attempt started successfully.'
        }, status=status.HTTP_201_CREATED)

    @extend_schema(summary="Get basic details of an attempt", responses={200: AttemptListSerializer})
    def retrieve(self, request, pk=None):
        """Get the current state of an attempt."""
        attempt = self.get_object()
        serializer = AttemptListSerializer(attempt)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Attempt retrieved.'
        })

    @extend_schema(summary="Submit an answer for a question", request=AttemptAnswerSubmitSerializer)
    @action(detail=True, methods=['POST'])
    def answer(self, request, pk=None):
        """Submit a choice for a specific question within the attempt."""
        attempt = self.get_object()

        serializer = AttemptAnswerSubmitSerializer(
            data=request.data,
            context={'attempt': attempt}
        )
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        choice = validated_data['choice']

        AttemptAnswer.objects.create(
            attempt=attempt,
            question=validated_data['question'],
            selected_choice=choice,
            is_correct=choice.is_correct,
            time_taken_seconds=validated_data['time_taken_seconds']
        )

        return Response({
            'success': True,
            'data': {'is_correct': choice.is_correct},
            'message': 'Answer submitted.'
        })

    @extend_schema(summary="Complete attempt and calculate score", responses={200: AttemptResultSerializer})
    @action(detail=True, methods=['POST'])
    def complete(self, request, pk=None):
        """Finish the attempt, calculate the score, and return full results."""
        attempt = self.get_object()

        if attempt.status != Attempt.Status.IN_PROGRESS:
            return Response({
                'success': False,
                'error': {'code': 'INVALID_STATE', 'message': 'Attempt is already completed or abandoned.'}
            }, status=status.HTTP_400_BAD_REQUEST)

        # Complete calculates score and updates Analytics
        attempt.complete()

        result_serializer = AttemptResultSerializer(attempt)
        return Response({
            'success': True,
            'data': result_serializer.data,
            'message': f'Attempt completed! Score: {attempt.score}%'
        })

    @extend_schema(summary="Get full results of a completed attempt", responses={200: AttemptResultSerializer})
    @action(detail=True, methods=['GET'])
    def results(self, request, pk=None):
        """Get detailed breakdown of answers and explanations for a completed attempt."""
        attempt = self.get_object()

        if attempt.status != Attempt.Status.COMPLETED:
            return Response({
                'success': False,
                'error': {'code': 'NOT_COMPLETED', 'message': 'Results are only available for completed attempts.'}
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = AttemptResultSerializer(attempt)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Results retrieved.'
        })

    @extend_schema(summary="Alias for history - list all past attempts")
    @action(detail=False, methods=['GET'])
    def history(self, request):
        """Paginated past attempts list (alias for list)."""
        return self.list(request)
