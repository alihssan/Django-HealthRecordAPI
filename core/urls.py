from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AuthViewSet,
    RegisterView,
    UserManagementViewSet,
    DoctorViewSet,
    PatientViewSet
)

router = DefaultRouter()
router.register(r'users', UserManagementViewSet)
router.register(r'doctors', DoctorViewSet, basename='doctors')
router.register(r'patients', PatientViewSet, basename='patients')



urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', AuthViewSet.as_view(), name='auth-login'),
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
] 