from django.contrib import admin
from .models import UserStat, TopicPerformance


@admin.register(UserStat)
class UserStatAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_quizzes_taken', 'average_score', 'best_score', 'streak_days', 'updated_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('updated_at',)


@admin.register(TopicPerformance)
class TopicPerformanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'topic', 'attempts_count', 'average_score', 'best_score')
    list_filter = ('topic',)
    search_fields = ('user__username', 'topic')
    readonly_fields = ('updated_at',)
