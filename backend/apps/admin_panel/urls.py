from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdminUserViewSet, AdminQuizViewSet, AdminStatsViewSet, AdminLeaderboardViewSet

router = DefaultRouter()
router.register(r'users', AdminUserViewSet, basename='admin-users')
router.register(r'quizzes', AdminQuizViewSet, basename='admin-quizzes')
router.register(r'stats', AdminStatsViewSet, basename='admin-stats')
router.register(r'leaderboards', AdminLeaderboardViewSet, basename='admin-leaderboards')

urlpatterns = [
    path('', include(router.urls)),
]
