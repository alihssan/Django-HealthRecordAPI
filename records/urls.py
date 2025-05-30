from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HealthRecordViewSet, DoctorViewSet, PatientViewSet

router = DefaultRouter()
router.register(r'records', HealthRecordViewSet)
router.register(r'doctors', DoctorViewSet, basename='doctor')
router.register(r'patients', PatientViewSet, basename='patient')

urlpatterns = [
    path('', include(router.urls)),
] 