from rest_framework import serializers
from .models import HealthRecord, DoctorAnnotation
from django.contrib.auth import get_user_model
from core.serializers import UserProfileSerializer

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role')

class HealthRecordSerializer(serializers.ModelSerializer):
    patient = UserProfileSerializer(read_only=True)
    assigned_doctors = UserProfileSerializer(many=True, read_only=True)
    annotations = DoctorAnnotationSerializer(many=True, read_only=True)
    doctor_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = HealthRecord
        fields = '__all__'
        read_only_fields = ('record_id', 'created_at', 'updated_at')

    def validate(self, attrs):
        # Ensure patient can only create records for themselves
        if self.context['request'].user.role == 'PATIENT':
            attrs['patient'] = self.context['request'].user
        return attrs

    def validate_attachments(self, value):
        if value:
            # Check file size (10MB limit)
            if value.size > 10 * 1024 * 1024:
                raise serializers.ValidationError("File size must be no more than 10MB")
            
            # Check file type
            ext = value.name.split('.')[-1].lower()
            if ext not in ['pdf', 'jpg', 'jpeg', 'png']:
                raise serializers.ValidationError("Only PDF and image files are allowed")
        return value

    def create(self, validated_data):
        doctor_ids = validated_data.pop('doctor_ids', [])
        record = HealthRecord.objects.create(**validated_data)
        if doctor_ids:
            record.assigned_doctors.set(doctor_ids)
        return record

    def update(self, instance, validated_data):
        doctor_ids = validated_data.pop('doctor_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if doctor_ids is not None:
            instance.assigned_doctors.set(doctor_ids)
        return instance

class DoctorAnnotationSerializer(serializers.ModelSerializer):
    doctor_name = serializers.SerializerMethodField()

    class Meta:
        model = DoctorAnnotation
        fields = ('id', 'content', 'doctor', 'doctor_name', 'created_at', 'updated_at')
        read_only_fields = ('doctor', 'created_at', 'updated_at')

    def get_doctor_name(self, obj):
        return f"{obj.doctor.first_name} {obj.doctor.last_name}" 