"""
Serializers for quizzes, questions, and choices.
"""
from rest_framework import serializers
from .models import Quiz, Question, Choice


class ChoiceSerializer(serializers.ModelSerializer):
    """Serialize basic choice info, hiding is_correct for quiz-taking."""

    class Meta:
        model = Choice
        fields = ('id', 'choice_text', 'order')


class ChoiceWithAnswerSerializer(serializers.ModelSerializer):
    """Serialize full choice info including is_correct (for results/admins)."""

    class Meta:
        model = Choice
        fields = ('id', 'choice_text', 'is_correct', 'order')


class QuestionSerializer(serializers.ModelSerializer):
    """Serialize question with its choices."""
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ('id', 'question_text', 'question_type', 'points', 'order', 'choices')
        # Note: explanation is explicitly excluded here; only included in results


class QuestionWithAnswerSerializer(QuestionSerializer):
    """Serialize question with correct answers and explanations."""
    choices = ChoiceWithAnswerSerializer(many=True, read_only=True)

    class Meta(QuestionSerializer.Meta):
        fields = QuestionSerializer.Meta.fields + ('explanation',)


class QuizListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing quizzes."""
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Quiz
        fields = (
            'id', 'title', 'topic', 'difficulty', 'question_count',
            'time_limit_minutes', 'status', 'created_by_username',
            'is_public', 'created_at', 'updated_at'
        )


class QuizDetailSerializer(QuizListSerializer):
    """Detailed serializer including questions if ready."""
    questions = serializers.SerializerMethodField()

    class Meta(QuizListSerializer.Meta):
        fields = QuizListSerializer.Meta.fields + ('questions', 'error_message', 'ai_model_used')

    def get_questions(self, obj):
        # Only return questions if the quiz is fully ready
        if obj.status == Quiz.Status.READY:
            questions = obj.get_questions_with_choices()
            # Admins see correct answers and explanations
            request = self.context.get('request')
            if request and hasattr(request, 'user') and request.user.role == 'admin':
                return QuestionWithAnswerSerializer(questions, many=True).data
            return QuestionSerializer(questions, many=True).data
        return []


class QuizCreateSerializer(serializers.ModelSerializer):
    """Serializer for requesting AI quiz generation."""

    class Meta:
        model = Quiz
        fields = ('title', 'topic', 'difficulty', 'question_count', 'time_limit_minutes', 'is_public')

    def validate_question_count(self, value):
        if not (1 <= value <= 50):
            raise serializers.ValidationError("Question count must be between 1 and 50.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        quiz = Quiz.objects.create(created_by=user, status=Quiz.Status.GENERATING, **validated_data)
        # Task scheduling happens in the view or signal to ensure transaction completes
        return quiz
