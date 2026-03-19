from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AnalyticsViewSet, QuizStatsViewSet

router = DefaultRouter()
router.register(r'quiz', QuizStatsViewSet, basename='quiz-stats')
router.register(r'', AnalyticsViewSet, basename='analytics')

urlpatterns = [
    path('', include(router.urls)),
]
