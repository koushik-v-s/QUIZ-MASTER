"""
URL configuration for quiz_app project.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView


def health_check(request):
    """Health check endpoint for Railway."""
    return JsonResponse({'status': 'healthy', 'success': True})


urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # Health Check
    path('api/v1/health/', health_check, name='health-check'),

    # API v1
    path('api/v1/auth/', include('apps.users.urls')),
    path('api/v1/quizzes/', include('apps.quizzes.urls')),
    path('api/v1/attempts/', include('apps.attempts.urls')),
    path('api/v1/analytics/', include('apps.analytics.urls')),
    path('api/v1/admin/', include('apps.admin_panel.urls')),

    # API Documentation
    path('api/v1/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/v1/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/v1/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
