from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserManagementViewSet, AuthViewSet, RegisterView, DoctorViewSet, PatientViewSet,AppointmentViewSet

router = DefaultRouter()
router.register(r'users', UserManagementViewSet, basename='users')
router.register(r'doctors', DoctorViewSet, basename='doctor')
router.register(r'patients', PatientViewSet, basename='patient')
router.register(r'appointments', AppointmentViewSet, basename='appointment')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', AuthViewSet.as_view(), name='auth-login'),
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
]