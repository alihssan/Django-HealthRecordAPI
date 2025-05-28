from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users to access the view.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser 

class IsDoctor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'DOCTOR'

class IsPatient(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'PATIENT' 