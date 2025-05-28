from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from .models import HealthRecord, DoctorAnnotation
from .serializers import (
    HealthRecordSerializer, 
    DoctorAnnotationSerializer,
    UserSerializer
)
from core.permissions import IsAdminUser, IsDoctor, IsPatient

User = get_user_model()

# Create your views here.

class HealthRecordViewSet(viewsets.ModelViewSet):
    queryset = HealthRecord.objects.all()
    serializer_class = HealthRecordSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        elif self.action in ['create', 'update', 'partial_update']:
            return [IsPatient()]
        elif self.action == 'add_annotation':
            return [IsDoctor()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return HealthRecord.objects.all()
        elif user.role == 'DOCTOR':
            return HealthRecord.objects.filter(doctor=user)
        elif user.role == 'PATIENT':
            return HealthRecord.objects.filter(patient=user)
        return HealthRecord.objects.none()

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.role == 'PATIENT' and instance.patient != request.user:
            return Response(
                {'message': 'You can only update your own records'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def add_annotation(self, request, pk=None):
        """Add annotation to a record (Doctor only)"""
        record = self.get_object()
        if record.doctor != request.user:
            return Response(
                {'message': 'You can only annotate records assigned to you'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = DoctorAnnotationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(record=record, doctor=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DoctorViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for listing doctors (Patient only)"""
    serializer_class = UserSerializer
    permission_classes = [IsPatient]  # Only patients can view doctors

    def get_queryset(self):
        return User.objects.filter(role='DOCTOR')

    @action(detail=True, methods=['get'])
    def records(self, request, pk=None):
        """Get all records for a specific doctor"""
        doctor = self.get_object()
        records = HealthRecord.objects.filter(doctor=doctor)
        serializer = HealthRecordSerializer(records, many=True)
        return Response(serializer.data)

class PatientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for listing assigned patients (Doctor only)"""
    serializer_class = UserSerializer
    permission_classes = [IsDoctor]  # Only doctors can view their patients

    def get_queryset(self):
        # Only show patients who have records assigned to this doctor
        return User.objects.filter(
            role='PATIENT',
            health_records__doctor=self.request.user
        ).distinct()

    @action(detail=True, methods=['get'])
    def records(self, request, pk=None):
        """Get all records for a specific patient"""
        patient = self.get_object()
        # Only show records assigned to this doctor
        records = HealthRecord.objects.filter(
            patient=patient,
            doctor=request.user
        )
        serializer = HealthRecordSerializer(records, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def annotations(self, request, pk=None):
        """Get all annotations for a specific patient's records"""
        patient = self.get_object()
        annotations = DoctorAnnotation.objects.filter(
            record__patient=patient,
            record__doctor=request.user
        )
        serializer = DoctorAnnotationSerializer(annotations, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def upload_attachment(self, request, pk=None):
        record = self.get_object()
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        file = request.FILES['file']
        record.attachments = file
        record.save()
        
        return Response({
            'message': 'File uploaded successfully',
            'file_url': record.attachments.url
        })
