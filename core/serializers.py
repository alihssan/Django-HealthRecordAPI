from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime, timedelta
from .models import DoctorAppointment
from records.models import HealthRecord

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 
                 'role', 'date_of_birth', 'phone_number', 'address', 
                 'location', 'available_days', 'appointment_duration', 
                 'max_patients_per_day', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate(self, attrs):
        if attrs.get('role') == User.Role.DOCTOR:
            if not attrs.get('available_days'):
                raise serializers.ValidationError({
                    'available_days': 'Available days are required for doctors'
                })
            if not attrs.get('appointment_duration'):
                raise serializers.ValidationError({
                    'appointment_duration': 'Appointment duration is required for doctors'
                })
            if not attrs.get('max_patients_per_day'):
                raise serializers.ValidationError({
                    'max_patients_per_day': 'Maximum patients per day is required for doctors'
                })
        return attrs

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 
                 'last_name', 'role', 'date_of_birth', 'phone_number', 
                 'address', 'location')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'phone_number',
            'address', 'location', 'date_of_birth',
            'appointment_duration', 'max_patients_per_day', 'available_days'
        ]
        extra_kwargs = {
            'email': {'required': False},
            'appointment_duration': {'required': False},
            'max_patients_per_day': {'required': False},
            'available_days': {'required': False}
        }

    def validate(self, data):
        # Only validate doctor-specific fields if the user is a doctor
        if self.instance.role == User.Role.DOCTOR:
            if 'max_patients_per_day' in data:
                if data['max_patients_per_day'] < 1 or data['max_patients_per_day'] > 50:
                    raise serializers.ValidationError(
                        {'max_patients_per_day': 'Maximum patients per day must be between 1 and 50'}
                    )
            
            if 'appointment_duration' in data:
                if data['appointment_duration'] < 15 or data['appointment_duration'] > 120:
                    raise serializers.ValidationError(
                        {'appointment_duration': 'Appointment duration must be between 15 and 120 minutes'}
                    )

        return data

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs['username'], password=attrs['password'])
        if not user:
            raise serializers.ValidationError('Invalid credentials')
        if not user.is_active:
            raise serializers.ValidationError('User account is disabled')
        
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=User.Role.choices)
    
    # Doctor-specific fields
    appointment_duration = serializers.IntegerField(required=False, allow_null=True)
    max_patients_per_day = serializers.IntegerField(required=False, allow_null=True)
    available_days = serializers.JSONField(required=False, allow_null=True)
    
    # Common fields
    phone_number = serializers.CharField(required=True)
    address = serializers.CharField(required=True)
    location = serializers.CharField(required=True)
    date_of_birth = serializers.DateField(required=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'password', 'first_name', 'last_name',
            'role', 'phone_number', 'address', 'location', 'date_of_birth',
            'appointment_duration', 'max_patients_per_day', 'available_days'
        ]

    def validate(self, data):
        role = data.get('role')
        
        # Validate doctor-specific fields only if role is DOCTOR
        if role == User.Role.DOCTOR:
            if not data.get('appointment_duration'):
                raise serializers.ValidationError(
                    {'appointment_duration': 'Appointment duration is required for doctors'}
                )
            if not data.get('max_patients_per_day'):
                raise serializers.ValidationError(
                    {'max_patients_per_day': 'Maximum patients per day is required for doctors'}
                )
            if not data.get('available_days'):
                raise serializers.ValidationError(
                    {'available_days': 'Available days are required for doctors'}
                )
            
            # Validate appointment_duration range
            if data['appointment_duration'] < 15 or data['appointment_duration'] > 120:
                raise serializers.ValidationError(
                    {'appointment_duration': 'Appointment duration must be between 15 and 120 minutes'}
                )
            
            # Validate max_patients_per_day range
            if data['max_patients_per_day'] < 1 or data['max_patients_per_day'] > 50:
                raise serializers.ValidationError(
                    {'max_patients_per_day': 'Maximum patients per day must be between 1 and 50'}
                )
            
            # Validate available_days structure
            available_days = data.get('available_days', {})
            if not isinstance(available_days, dict):
                raise serializers.ValidationError(
                    {'available_days': 'Available days must be a valid JSON object'}
                )
            
            for day, schedule in available_days.items():
                if not isinstance(schedule, dict):
                    raise serializers.ValidationError(
                        {'available_days': f'Invalid schedule format for {day}'}
                    )
                if not all(key in schedule for key in ['start_time', 'end_time', 'is_available']):
                    raise serializers.ValidationError(
                        {'available_days': f'Missing required fields in schedule for {day}'}
                    )
        
        return data

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class DoctorAvailabilityUpdateSerializer(serializers.ModelSerializer):
    available_days = serializers.JSONField(required=True)
    appointment_duration = serializers.IntegerField(required=True)
    max_patients_per_day = serializers.IntegerField(required=True)

    class Meta:
        model = User
        fields = ['available_days', 'appointment_duration', 'max_patients_per_day']

    def validate_available_days(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Available days must be a valid JSON object")
        
        valid_days = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY']
        
        for day, schedule in value.items():
            if day not in valid_days:
                raise serializers.ValidationError(f"Invalid day: {day}")
            
            if not isinstance(schedule, dict):
                raise serializers.ValidationError(f"Invalid schedule format for {day}")
            
            required_fields = ['start_time', 'end_time', 'is_available']
            if not all(field in schedule for field in required_fields):
                raise serializers.ValidationError(f"Missing required fields in schedule for {day}")
            
            if not isinstance(schedule['is_available'], bool):
                raise serializers.ValidationError(f"is_available must be boolean for {day}")
            
            try:
                start_time = datetime.strptime(schedule['start_time'], '%H:%M').time()
                end_time = datetime.strptime(schedule['end_time'], '%H:%M').time()
                if start_time >= end_time:
                    raise serializers.ValidationError(f"End time must be after start time for {day}")
            except ValueError:
                raise serializers.ValidationError(f"Invalid time format for {day}. Use HH:MM format")
        
        return value

    def validate_appointment_duration(self, value):
        if value < 15 or value > 120:
            raise serializers.ValidationError("Appointment duration must be between 15 and 120 minutes")
        return value

    def validate_max_patients_per_day(self, value):
        if value < 1 or value > 50:
            raise serializers.ValidationError("Maximum patients per day must be between 1 and 50")
        return value

class AppointmentBookingSerializer(serializers.ModelSerializer):
    doctor = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role=User.Role.DOCTOR)
    )
    appointment_date = serializers.DateField()
    start_time = serializers.TimeField(format='%H:%M')
    end_time = serializers.TimeField(format='%H:%M')
    notes = serializers.CharField(required=False, allow_blank=True)
    doctor_name = serializers.SerializerMethodField(read_only=True)
    doctor_specialization = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = DoctorAppointment
        fields = [
            'id', 'doctor', 'doctor_name', 'doctor_specialization',
            'appointment_date', 'start_time', 'end_time', 'notes',
            'status'
        ]
        read_only_fields = ['status', 'id']

    def get_doctor_name(self, obj):
        if isinstance(obj, dict):
            doctor = obj.get('doctor')
        else:
            doctor = obj.doctor
        return f"{doctor.first_name} {doctor.last_name}" if doctor else None

    def get_doctor_specialization(self, obj):
        if isinstance(obj, dict):
            doctor = obj.get('doctor')
        else:
            doctor = obj.doctor
        return doctor.specialization if doctor else None

    def validate(self, data):
        # Add the current user as the patient
        data['patient'] = self.context['request'].user

        # Validate appointment date is not in the past
        if data['appointment_date'] < datetime.now().date():
            raise serializers.ValidationError("Cannot book appointments in the past")

        # Validate end time is after start time
        if data['end_time'] <= data['start_time']:
            raise serializers.ValidationError("End time must be after start time")

        # Validate appointment duration matches doctor's setting
        doctor = data['doctor']
        appointment_duration = (datetime.combine(datetime.today(), data['end_time']) - 
                              datetime.combine(datetime.today(), data['start_time'])).total_seconds() / 60
        
        if appointment_duration != doctor.appointment_duration:
            raise serializers.ValidationError(
                f"Appointment duration must be {doctor.appointment_duration} minutes"
            )

        # Validate doctor's availability
        day_of_week = data['appointment_date'].strftime('%A').upper()
        availability = doctor.get_availability(day_of_week)
        
        if not availability or not availability.get('is_available', False):
            raise serializers.ValidationError(f"Doctor is not available on {day_of_week}")

        try:
            # Convert string times to time objects for comparison
            doctor_start_time = datetime.strptime(availability['start_time'], '%H:%M').time()
            doctor_end_time = datetime.strptime(availability['end_time'], '%H:%M').time()
            
            # Ensure start_time and end_time are time objects
            if isinstance(data['start_time'], str):
                data['start_time'] = datetime.strptime(data['start_time'], '%H:%M').time()
            if isinstance(data['end_time'], str):
                data['end_time'] = datetime.strptime(data['end_time'], '%H:%M').time()
            
            if (data['start_time'] < doctor_start_time or 
                data['end_time'] > doctor_end_time):
                raise serializers.ValidationError(
                    "Appointment time must be within doctor's working hours"
                )
        except (ValueError, KeyError) as e:
            raise serializers.ValidationError(f'Invalid time format in doctor availability: {str(e)}')

        # Check for overlapping appointments
        overlapping = DoctorAppointment.objects.filter(
            doctor=doctor,
            appointment_date=data['appointment_date'],
            status=User.AppointmentStatus.SCHEDULED,
            start_time__lt=data['end_time'],
            end_time__gt=data['start_time']
        ).exclude(id=self.instance.id if self.instance else None)

        if overlapping.exists():
            raise serializers.ValidationError("This time slot overlaps with another appointment")

        return data

    def create(self, validated_data):
        try:
            # Ensure times are in the correct format
            if isinstance(validated_data['start_time'], str):
                validated_data['start_time'] = datetime.strptime(validated_data['start_time'], '%H:%M').time()
            if isinstance(validated_data['end_time'], str):
                validated_data['end_time'] = datetime.strptime(validated_data['end_time'], '%H:%M').time()

            # Create the appointment
            appointment = DoctorAppointment.objects.create(**validated_data)
            
            # Create initial health record
            health_record = HealthRecord.objects.create(
                record_type=HealthRecord.RecordType.CONSULTATION,
                title=f"Appointment with Dr. {appointment.doctor.get_full_name()}",
                description=f"Initial consultation appointment scheduled for {appointment.appointment_date}",
                patient=validated_data['patient'],
                doctor=appointment.doctor
            )
            
            return appointment
        except Exception as e:
            raise serializers.ValidationError(f"Error creating appointment: {str(e)}")

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Add additional data to the response
        data['doctor_name'] = self.get_doctor_name(instance)
        data['doctor_specialization'] = self.get_doctor_specialization(instance)
        return data

class DoctorAvailabilityResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'available_days', 
                 'appointment_duration', 'max_patients_per_day']

class AppointmentResponseSerializer(serializers.ModelSerializer):
    doctor = UserSerializer(read_only=True)
    patient = UserSerializer(read_only=True)

    class Meta:
        model = DoctorAppointment
        fields = ['id', 'doctor', 'patient', 'appointment_date', 
                 'start_time', 'end_time', 'status', 'notes', 
                 'created_at', 'updated_at'] 