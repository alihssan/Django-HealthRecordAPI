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
    RegisterSerializer
)
from .permissions import IsAdminUser, IsDoctor, IsPatient

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
            return Response({
                'message': 'User registered successfully',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserManagementViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing users
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsAdminUser()]
        elif self.action == 'list':
            return [IsAdminUser()]
        return [permissions.IsAuthenticated()]

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
        """Get all doctors"""
        doctors = User.objects.filter(role=User.Role.DOCTOR)
        serializer = self.get_serializer(doctors, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def patients(self, request):
        """Get all patients"""
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

    def get_queryset(self):
        return User.objects.filter(role=User.Role.DOCTOR)

    @action(detail=False, methods=['get'])
    def my_patients(self, request):
        """Get all patients assigned to the doctor"""
        patients = User.objects.filter(assigned_doctor=request.user)
        serializer = self.get_serializer(patients, many=True)
        return Response(serializer.data)

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
