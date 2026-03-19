from django.contrib import admin
from .models import Quiz, Question, Choice


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0
    show_change_link = True


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 0


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'topic', 'difficulty', 'question_count', 'status', 'created_by', 'is_public', 'created_at')
    list_filter = ('status', 'difficulty', 'is_public', 'created_at')
    search_fields = ('title', 'topic', 'created_by__username')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text_short', 'quiz', 'question_type', 'order', 'points')
    list_filter = ('question_type',)
    search_fields = ('question_text',)
    inlines = [ChoiceInline]

    def question_text_short(self, obj):
        return obj.question_text[:80] + '...' if len(obj.question_text) > 80 else obj.question_text
    question_text_short.short_description = 'Question'


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('choice_text', 'question', 'is_correct', 'order')
    list_filter = ('is_correct',)
    search_fields = ('choice_text',)
