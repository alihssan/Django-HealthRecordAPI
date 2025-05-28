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
from core.models import User

User = get_user_model()

# Create your views here.

class PatientHealthRecordViewSet(viewsets.ModelViewSet):
    """
    ViewSet for patients and admins to view and update health records.
    """
    serializer_class = HealthRecordSerializer
    permission_classes = [permissions.IsAuthenticated]  # Base permission

    def get_permissions(self):
        """
        Allow only patients and admins to access these endpoints.
        """
        if self.request.user.role in ['PATIENT', 'ADMIN']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]  # Will be checked in get_queryset

    def get_queryset(self):
        """
        Return health records based on user role:
        - Patients can only see their own records
        - Admins can see all records
        """
        user = self.request.user
        if user.role == 'ADMIN':
            return HealthRecord.objects.all()
        elif user.role == 'PATIENT':
            return HealthRecord.objects.filter(patient=user)
        return HealthRecord.objects.none()

    def perform_create(self, serializer):
        """
        Automatically set the patient to the authenticated user when creating a record.
        """
        serializer.save(patient=self.request.user)

    def update(self, request, *args, **kwargs):
        """
        Ensure patients can only update their own records.
        Admins can update any record.
        """
        instance = self.get_object()
        if request.user.role == 'PATIENT' and instance.patient != request.user:
            return Response(
                {'detail': 'You can only update your own records.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=['get'])
    def record_details(self, request, pk=None):
        """
        Get detailed information about a specific record including doctor and patient details.
        """
        record = self.get_object()
        
        # Check permissions
        if request.user.role == 'PATIENT' and record.patient != request.user:
            return Response(
                {'detail': 'You can only view your own records.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Get doctor and patient details
        doctor_details = None
        if record.doctor:
            doctor_details = {
                'id': record.doctor.id,
                'username': record.doctor.username,
                'email': record.doctor.email,
                'specialization': record.doctor.specialization,
                'phone_number': record.doctor.phone_number,
                'location': record.doctor.location
            }

        patient_details = {
            'id': record.patient.id,
            'username': record.patient.username,
            'email': record.patient.email,
            'phone_number': record.patient.phone_number,
            'date_of_birth': record.patient.date_of_birth
        }

        # Get record details
        record_data = self.get_serializer(record).data

        # Combine all details
        response_data = {
            'record': record_data,
            'doctor': doctor_details,
            'patient': patient_details
        }

        return Response(response_data)

    @action(detail=False, methods=['get'])
    def my_records(self, request):
        """
        Get all records for the authenticated patient with doctor details.
        """
        records = self.get_queryset()
        records_with_details = []

        for record in records:
            record_data = self.get_serializer(record).data
            
            # Add doctor details if available
            if record.doctor:
                record_data['doctor_details'] = {
                    'id': record.doctor.id,
                    'username': record.doctor.username,
                    'specialization': record.doctor.specialization,
                    'location': record.doctor.location
                }
            
            records_with_details.append(record_data)

        return Response(records_with_details)

    @action(detail=False, methods=['get'])
    def records_by_type(self, request):
        """
        Get records filtered by type with doctor details.
        """
        record_type = request.query_params.get('type', None)
        if not record_type:
            return Response(
                {'error': 'Please provide a record type'},
                status=status.HTTP_400_BAD_REQUEST
            )

        records = self.get_queryset().filter(record_type=record_type)
        records_with_details = []

        for record in records:
            record_data = self.get_serializer(record).data
            
            # Add doctor details if available
            if record.doctor:
                record_data['doctor_details'] = {
                    'id': record.doctor.id,
                    'username': record.doctor.username,
                    'specialization': record.doctor.specialization,
                    'location': record.doctor.location
                }
            
            records_with_details.append(record_data)

        return Response(records_with_details)

    @action(detail=True, methods=['post'])
    def upload_attachment(self, request, pk=None):
        """
        Allow patients to upload attachments to their records.
        """
        record = self.get_object()
        if request.user.role == 'PATIENT' and record.patient != request.user:
            return Response(
                {'detail': 'You can only upload attachments to your own records.'},
                status=status.HTTP_403_FORBIDDEN
            )

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
