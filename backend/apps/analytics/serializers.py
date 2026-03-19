"""
Serializers for aggregated analytics and leaderboard data.
"""
from rest_framework import serializers
from .models import UserStat, TopicPerformance, QuizStat


class UserStatSerializer(serializers.ModelSerializer):
    """Serialize overall user stats."""
    username = serializers.CharField(source='user.username', read_only=True)
    avatar_url = serializers.CharField(source='user.avatar_url', read_only=True)

    class Meta:
        model = UserStat
        fields = (
            'username', 'avatar_url', 'total_quizzes_taken', 'total_quizzes_created',
            'average_score', 'best_score', 'total_time_spent_seconds',
            'strongest_topic', 'weakest_topic', 'streak_days', 'last_activity_date'
        )


class TopicPerformanceSerializer(serializers.ModelSerializer):
    """Serialize per-topic user performance."""

    class Meta:
        model = TopicPerformance
        fields = ('topic', 'attempts_count', 'average_score', 'best_score')


class LeaderboardSerializer(serializers.ModelSerializer):
    """Serialize leaderboard records. Only showing public-friendly info."""
    username = serializers.CharField(source='user.username', read_only=True)
    avatar_url = serializers.CharField(source='user.avatar_url', read_only=True)
    overall_rating = serializers.SerializerMethodField()

    class Meta:
        model = UserStat
        fields = (
            'username', 'avatar_url', 'total_quizzes_taken',
            'average_score', 'streak_days', 'overall_rating'
        )

    def get_overall_rating(self, obj):
        weight_volume = obj.total_quizzes_taken * 5
        weight_accuracy = obj.average_score * 2
        return min(round(weight_volume + weight_accuracy), 1000)


class ScoreHistorySerializer(serializers.Serializer):
    """Serializer to represent chronological quiz scores for charts."""
    date = serializers.DateTimeField()
    score = serializers.FloatField()
    quiz_title = serializers.CharField()
    topic = serializers.CharField()


class QuizStatSerializer(serializers.ModelSerializer):
    """Serialize quiz-level stats for admins."""
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    quiz_topic = serializers.CharField(source='quiz.topic', read_only=True)

    class Meta:
        model = QuizStat
        fields = (
            'quiz_title', 'quiz_topic', 'total_attempts',
            'average_score', 'highest_score', 'lowest_score',
            'completion_rate', 'updated_at'
        )
