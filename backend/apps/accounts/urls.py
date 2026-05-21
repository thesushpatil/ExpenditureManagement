"""
URL patterns for authentication endpoints.

Endpoints:
    POST   /api/v1/auth/register/         - Register new user
    POST   /api/v1/auth/login/            - Get JWT tokens (login)
    POST   /api/v1/auth/login/refresh/    - Refresh access token
    GET    /api/v1/auth/profile/          - Get user profile
    PATCH  /api/v1/auth/profile/          - Update user profile
    POST   /api/v1/auth/change-password/  - Change password
    POST   /api/v1/auth/logout/           - Logout (blacklist token)
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, ProfileView, ChangePasswordView, LogoutView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('login/', TokenObtainPairView.as_view(), name='auth-login'),
    path('login/refresh/', TokenRefreshView.as_view(), name='auth-token-refresh'),
    path('profile/', ProfileView.as_view(), name='auth-profile'),
    path('change-password/', ChangePasswordView.as_view(), name='auth-change-password'),
    path('logout/', LogoutView.as_view(), name='auth-logout'),
]
