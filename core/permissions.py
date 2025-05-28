from rest_framework import permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import get_user_model

User = get_user_model()

class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users to access the view.
    """
    def has_permission(self, request, view):
        # Get the user from the JWT token
        jwt_authenticator = JWTAuthentication()
        try:
            # This will validate the token and return the user
            user_auth_tuple = jwt_authenticator.authenticate(request)
            if user_auth_tuple is None:
                return False
            user, _ = user_auth_tuple
            return user.is_superuser
        except Exception:
            return False

class IsDoctor(permissions.BasePermission):
    def has_permission(self, request, view):
        jwt_authenticator = JWTAuthentication()
        try:
            user_auth_tuple = jwt_authenticator.authenticate(request)
            if user_auth_tuple is None:
                return False
            user, _ = user_auth_tuple
            return user.role == 'DOCTOR'
        except Exception:
            return False

class IsPatient(permissions.BasePermission):
    def has_permission(self, request, view):
        jwt_authenticator = JWTAuthentication()
        try:
            user_auth_tuple = jwt_authenticator.authenticate(request)
            if user_auth_tuple is None:
                return False
            user, _ = user_auth_tuple
            return user.role == 'PATIENT'
        except Exception:
            return False 