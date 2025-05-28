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

    def get_queryset(self):
        return User.objects.filter(role=User.Role.PATIENT)

    @action(detail=False, methods=['get'])
    def my_doctor(self, request):
        """Get the patient's assigned doctor"""
        doctor = request.user.assigned_doctor
        if doctor:
            serializer = self.get_serializer(doctor)
            return Response(serializer.data)
        return Response({'message': 'No doctor assigned'}, status=status.HTTP_404_NOT_FOUND)
