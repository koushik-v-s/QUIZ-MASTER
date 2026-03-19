from django.contrib import admin
from .models import Attempt, AttemptAnswer


class AttemptAnswerInline(admin.TabularInline):
    model = AttemptAnswer
    extra = 0
    readonly_fields = ('question', 'selected_choice', 'is_correct', 'time_taken_seconds', 'answered_at')


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'status', 'score', 'total_points_earned', 'total_points_possible', 'started_at', 'completed_at')
    list_filter = ('status', 'started_at')
    search_fields = ('user__username', 'user__email', 'quiz__title')
    ordering = ('-started_at',)
    readonly_fields = ('id', 'started_at')
    inlines = [AttemptAnswerInline]


@admin.register(AttemptAnswer)
class AttemptAnswerAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question_short', 'selected_choice', 'is_correct', 'time_taken_seconds')
    list_filter = ('is_correct',)
    search_fields = ('question__question_text',)

    def question_short(self, obj):
        return obj.question.question_text[:60]
    question_short.short_description = 'Question'
