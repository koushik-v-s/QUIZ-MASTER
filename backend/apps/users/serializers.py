"""
Serializers for User authentication and profile management.
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from apps.analytics.models import UserStat


class UserProfileSerializer(serializers.ModelSerializer):
    """Serialize basic user profile information."""

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'role', 'avatar_url', 'date_joined')
        read_only_fields = ('id', 'email', 'role', 'date_joined')


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for registering a new user."""

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'password')

    def create(self, validated_data):
        import logging
        logger = logging.getLogger(__name__)

        # Warn if client tried to send a 'role' field (role tampering attempt)
        request = self.context.get('request')
        if request and 'role' in request.data:
            logger.warning(
                f"Role tampering attempt during registration: "
                f"email={validated_data['email']}, attempted_role={request.data['role']}"
            )

        # Always create with role='user' regardless of what client sends
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password']
        )
        # Initialize an empty UserStat record for the new user
        UserStat.refresh_for_user(user)
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom login serializer to include user details in the response."""

    def validate(self, attrs):
        data = super().validate(attrs)
        # Add user basic info to the token response
        data['user'] = UserProfileSerializer(self.user).data
        return data


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change endpoint."""

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "New passwords do not match."})
        return data

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is not correct")
        return value

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
