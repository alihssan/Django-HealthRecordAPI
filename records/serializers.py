from rest_framework import serializers
from .models import HealthRecord, DoctorAnnotation
from core.serializers import UserProfileSerializer

class DoctorAnnotationSerializer(serializers.ModelSerializer):
    doctor = UserProfileSerializer(read_only=True)

    class Meta:
        model = DoctorAnnotation
        fields = ('id', 'doctor', 'content', 'created_at', 'updated_at')
        read_only_fields = ('id', 'doctor', 'created_at', 'updated_at')

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
        fields = ('id', 'patient', 'assigned_doctors', 'record_type', 'title',
                 'description', 'date', 'created_at', 'updated_at', 'is_private',
                 'attachments', 'annotations', 'doctor_ids')
        read_only_fields = ('id', 'patient', 'created_at', 'updated_at')

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