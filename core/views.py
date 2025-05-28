from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import (
    UserSerializer, 
    UserCreateSerializer, 
    UserUpdateSerializer,
    LoginSerializer,
    RegisterSerializer,
    DoctorAvailabilityUpdateSerializer
)
from .permissions import IsAdminUser, IsDoctor, IsPatient
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import datetime, timedelta
from .models import DoctorAppointment
from records.models import HealthRecord
from .serializers import (
    AppointmentBookingSerializer,
    AppointmentResponseSerializer,
    DoctorAvailabilityResponseSerializer
)
from .permissions import IsPatient
import time

User = get_user_model()

class AuthViewSet(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Customize response based on user role
            response_data = {
                'message': 'User registered successfully',
                'user': UserSerializer(user).data
            }
            
            # If user is a patient, remove doctor-specific fields
            if user.role == User.Role.PATIENT:
                response_data['user'].pop('appointment_duration', None)
                response_data['user'].pop('max_patients_per_day', None)
                response_data['user'].pop('available_days', None)
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserManagementViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing users
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.action in ['list', 'destroy']:
            return [IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        if self.action == 'list':
            # Only admin can see all users
            if not self.request.user.is_superuser:
                return User.objects.none()
            return User.objects.all()
        return User.objects.all()

    def list(self, request, *args, **kwargs):
        # Additional check for admin role
        if not request.user.is_superuser:
            return Response(
                {'message': 'Only administrators can view all users'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().list(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'message': 'User created successfully',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        # Users can only update their own profile
        if not request.user.is_superuser and request.user.id != int(kwargs['pk']):
            return Response(
                {'message': 'You can only update your own profile'},
                status=status.HTTP_403_FORBIDDEN
            )

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'message': 'User updated successfully',
            'user': UserSerializer(user).data
        })

    def destroy(self, request, *args, **kwargs):
        # Only admin can delete users
        if not request.user.is_superuser:
            return Response(
                {'message': 'Only administrators can delete users'},
                status=status.HTTP_403_FORBIDDEN
            )
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'message': 'User deleted successfully'
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def doctors(self, request):
        """Get all doctors (Admin only)"""
        if not request.user.is_superuser:
            return Response(
                {'message': 'Only administrators can view all doctors'},
                status=status.HTTP_403_FORBIDDEN
            )
        doctors = User.objects.filter(role=User.Role.DOCTOR)
        serializer = self.get_serializer(doctors, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def patients(self, request):
        """Get all patients (Admin only)"""
        if not request.user.is_superuser:
            return Response(
                {'message': 'Only administrators can view all patients'},
                status=status.HTTP_403_FORBIDDEN
            )
        patients = User.objects.filter(role=User.Role.PATIENT)
        serializer = self.get_serializer(patients, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class DoctorViewSet(viewsets.ModelViewSet):
    """
    API endpoint for doctor-specific operations
    """
    permission_classes = [IsDoctor]
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        return User.objects.filter(role=User.Role.DOCTOR)

    def get_serializer_class(self):
        if self.action == 'update_availability':
            return DoctorAvailabilityUpdateSerializer
        elif self.action == 'update_profile':
            return UserUpdateSerializer
        return UserSerializer

    @action(detail=False, methods=['get'])
    def my_patients(self, request):
        """Get all patients assigned to the doctor"""
        try:
            # Try to get patients through the reverse relationship
            patients = User.objects.filter(role=User.Role.PATIENT, doctor_appointments__doctor=request.user).distinct()
            if not patients.exists():
                return Response({
                    'message': 'No patients assigned yet',
                    'patients': []
                })
            
            serializer = self.get_serializer(patients, many=True)
            return Response({
                'message': 'Patients retrieved successfully',
                'patients': serializer.data
            })
        except Exception as e:
            return Response({
                'message': 'Error retrieving patients',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get', 'put'])
    def availability(self, request):
        """Get or update doctor's availability"""
        doctor = request.user
        
        if request.method == 'GET':
            serializer = DoctorAvailabilityUpdateSerializer(doctor)
            return Response(serializer.data)
        
        # PUT request
        serializer = DoctorAvailabilityUpdateSerializer(doctor, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Availability updated successfully',
                'availability': serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def profile(self, request):
        """Get doctor's profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put'])
    def update_profile(self, request):
        """Update doctor's profile"""
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'Profile updated successfully',
                'user': UserSerializer(user).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PatientViewSet(viewsets.ModelViewSet):
    """
    API endpoint for patient-specific operations
    """
    permission_classes = [IsPatient]
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        return User.objects.filter(role=User.Role.PATIENT)

    def get_serializer_class(self):
        if self.action == 'update_profile':
            return UserUpdateSerializer
        return UserSerializer

    @action(detail=False, methods=['get'])
    def profile(self, request):
        """Get patient's profile"""
        try:
            serializer = self.get_serializer(request.user)
            return Response({
                'message': 'Profile retrieved successfully',
                'user': serializer.data
            })
        except Exception as e:
            return Response({
                'message': 'Error retrieving profile',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['put'])
    def update_profile(self, request):
        """Update patient's profile"""
        try:
            serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
            if serializer.is_valid():
                user = serializer.save()
                return Response({
                    'message': 'Profile updated successfully',
                    'user': UserSerializer(user).data
                })
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'message': 'Error updating profile',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def my_doctor(self, request):
        """Get the patient's assigned doctor"""
        try:
            doctor = User.objects.filter(
                role=User.Role.DOCTOR,
                doctor_appointments__patient=request.user
            ).first()
            
            if doctor:
                serializer = self.get_serializer(doctor)
                return Response({
                    'message': 'Doctor retrieved successfully',
                    'doctor': serializer.data
                })
            return Response({
                'message': 'No doctor assigned yet',
                'doctor': None
            })
        except Exception as e:
            return Response({
                'message': 'Error retrieving doctor',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AppointmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling appointment-related operations
    """
    permission_classes = [IsAuthenticated]
    serializer_class = AppointmentResponseSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == User.Role.DOCTOR:
            return DoctorAppointment.objects.filter(doctor=user)
        elif user.role == User.Role.PATIENT:
            return DoctorAppointment.objects.filter(patient=user)
        return DoctorAppointment.objects.none()

    @action(detail=False, methods=['get'])
    def available_doctors(self, request):
        """Get list of available doctors with their schedules"""
        try:
            doctors = User.objects.filter(role=User.Role.DOCTOR)
            doctors_data = []

            for doctor in doctors:
                availability = doctor.available_days
                doctors_data.append({
                    'id': doctor.id,
                    'name': f"{doctor.first_name} {doctor.last_name}",
                    'specialization': doctor.specialization,
                    'availability': availability,
                    'appointment_duration': doctor.appointment_duration,
                    'max_patients_per_day': doctor.max_patients_per_day
                })

            return Response({
                'message': 'Available doctors retrieved successfully',
                'doctors': doctors_data
            })

        except Exception as e:
            return Response({
                'message': 'Error retrieving available doctors',
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def doctor_availability(self, request):
        """Get specific doctor's availability for a date range"""
        doctor_id = request.query_params.get('doctor_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not all([doctor_id, start_date, end_date]):
            return Response({
                'message': 'Missing required parameters'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            doctor = User.objects.get(id=doctor_id, role=User.Role.DOCTOR)
            
            # Get existing appointments for the date range
            existing_appointments = DoctorAppointment.objects.filter(
                doctor=doctor,
                appointment_date__range=[start_date, end_date],
                status=User.AppointmentStatus.SCHEDULED
            )

            # Get doctor's availability
            availability = doctor.available_days

            return Response({
                'message': 'Doctor availability retrieved successfully',
                'doctor': {
                    'id': doctor.id,
                    'name': f"{doctor.first_name} {doctor.last_name}",
                    'availability': availability,
                    'existing_appointments': [
                        {
                            'date': apt.appointment_date,
                            'start_time': apt.start_time,
                            'end_time': apt.end_time
                        } for apt in existing_appointments
                    ]
                }
            })

        except User.DoesNotExist:
            return Response({
                'message': 'Doctor not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'message': 'Error retrieving doctor availability',
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def book(self, request):
        """Book a new appointment"""
        try:
            # Validate and create appointment
            serializer = AppointmentBookingSerializer(
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            appointment = serializer.save()

            # Create empty health record for the appointment
            health_record = HealthRecord.objects.create(
                record_id=f"HR{int(time.time())}",
                record_type=HealthRecord.RecordType.CONSULTATION,
                title=f"Appointment with Dr. {appointment.doctor.get_full_name()}",
                description="",  # Empty description
                patient=request.user,
                doctor=appointment.doctor,
                attachments=None  # No attachments initially
            )

            return Response({
                'message': 'Appointment booked successfully',
                'appointment': AppointmentResponseSerializer(appointment).data,
                'health_record': {
                    'id': health_record.record_id,
                    'title': health_record.title,
                    'type': health_record.record_type,
                    'description': health_record.description,
                    'created_at': health_record.created_at
                }
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'message': 'Error booking appointment',
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an existing appointment"""
        try:
            appointment = self.get_object()
            
            # Check if appointment can be cancelled (e.g., not in the past)
            if appointment.appointment_date < timezone.now().date():
                return Response({
                    'message': 'Cannot cancel past appointments'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Update appointment status
            appointment.status = User.AppointmentStatus.CANCELLED
            appointment.save()

            return Response({
                'message': 'Appointment cancelled successfully',
                'appointment': AppointmentResponseSerializer(appointment).data
            })

        except Exception as e:
            return Response({
                'message': 'Error cancelling appointment',
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def reschedule(self, request, pk=None):
        """Reschedule an existing appointment"""
        try:
            appointment = self.get_object()
            
            # Validate new appointment time
            serializer = AppointmentBookingSerializer(
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            
            # Update appointment
            appointment.appointment_date = serializer.validated_data['appointment_date']
            appointment.start_time = serializer.validated_data['start_time']
            appointment.end_time = serializer.validated_data['end_time']
            appointment.save()

            return Response({
                'message': 'Appointment rescheduled successfully',
                'appointment': AppointmentResponseSerializer(appointment).data
            })

        except Exception as e:
            return Response({
                'message': 'Error rescheduling appointment',
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)