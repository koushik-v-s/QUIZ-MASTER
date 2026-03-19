"""
Views for authentication and user management endpoints.
"""
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema

from .models import User
from .serializers import (
    UserRegistrationSerializer,
    UserProfileSerializer,
    CustomTokenObtainPairSerializer,
    ChangePasswordSerializer
)


class RegisterView(generics.CreateAPIView):
    """Register a new user and return user details + JWT tokens."""

    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer

    @extend_schema(summary="Register a new user")
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate tokens for the new user automatically
        refresh = RefreshToken.for_user(user)

        response_data = {
            'success': True,
            'data': {
                'user': UserProfileSerializer(user).data,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            },
            'message': 'User registered successfully.'
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    """Authenticate and return JWT token pair + user details."""

    permission_classes = (AllowAny,)
    serializer_class = CustomTokenObtainPairSerializer

    @extend_schema(summary="Login (obtain JWT pair)")
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            return Response({
                'success': True,
                'data': response.data,
                'message': 'Login successful.'
            })
        return response


class LogoutView(APIView):
    """Blacklist the provided refresh token to logout."""

    permission_classes = (IsAuthenticated,)

    @extend_schema(summary="Logout (blacklist refresh token)", request={'application/json': {'type': 'object', 'properties': {'refresh': {'type': 'string'}}}})
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response(
                    {'success': False, 'error': {'code': 'VALIDATION_ERROR', 'message': 'Refresh token is required.'}},
                    status=status.HTTP_400_BAD_REQUEST
                )
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {'success': True, 'data': None, 'message': 'Successfully logged out.'},
                status=status.HTTP_200_OK
            )
        except Exception:
            return Response(
                {'success': False, 'error': {'code': 'INVALID_TOKEN', 'message': 'Refresh token is invalid or expired.'}},
                status=status.HTTP_400_BAD_REQUEST
            )


class MeView(generics.RetrieveUpdateAPIView):
    """Get or update current authenticated user's profile."""

    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user

    @extend_schema(summary="Get current user profile")
    def get(self, request, *args, **kwargs):
        return Response({
            'success': True,
            'data': self.get_serializer(self.get_object()).data,
            'message': 'Profile retrieved successfully.'
        })

    @extend_schema(summary="Patch current user profile")
    def patch(self, request, *args, **kwargs):
        kwargs['partial'] = True
        response = super().update(request, *args, **kwargs)
        return Response({
            'success': True,
            'data': response.data,
            'message': 'Profile updated successfully.'
        })

    @extend_schema(summary="Update current user profile")
    def put(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({
            'success': True,
            'data': response.data,
            'message': 'Profile updated successfully.'
        })


class ChangePasswordView(generics.UpdateAPIView):
    """Change current user's password."""

    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer

    def get_object(self):
        return self.request.user

    @extend_schema(summary="Change password")
    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'success': True,
            'data': None,
            'message': 'Password changed successfully.'
        })
