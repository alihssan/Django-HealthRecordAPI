from django.db import models
from core.models import User
import os
from django.core.exceptions import ValidationError

def health_record_file_path(instance, filename):
    # Generate file path: health_records/record_id/filename
    return f'health_records/{instance.record_id}/{filename}'

class HealthRecord(models.Model):
    class RecordType(models.TextChoices):
        CONSULTATION = 'CONSULTATION', 'Consultation'
        LAB_RESULT = 'LAB_RESULT', 'Lab Result'
        PRESCRIPTION = 'PRESCRIPTION', 'Prescription'
        VACCINATION = 'VACCINATION', 'Vaccination'
        OTHER = 'OTHER', 'Other'

    record_id = models.AutoField(primary_key=True)
    record_type = models.CharField(
        max_length=20,
        choices=RecordType.choices,
        default=RecordType.CONSULTATION
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='health_records',
        limit_choices_to={'role': User.Role.PATIENT}
    )
    doctor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='assigned_records',
        limit_choices_to={'role': User.Role.DOCTOR},
        null=True,
        blank=True
    )
    attachments = models.FileField(
        upload_to=health_record_file_path,
        blank=True,
        null=True,
        help_text='Upload images or PDF files'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'health_records'
        verbose_name = 'Health Record'
        verbose_name_plural = 'Health Records'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.record_id} - {self.title} - {self.patient.username}"

    def clean(self):
        if self.doctor and self.doctor.role != User.Role.DOCTOR:
            raise ValidationError('Assigned user must be a doctor')
        if self.patient.role != User.Role.PATIENT:
            raise ValidationError('Patient must be a patient')

    def save(self, *args, **kwargs):
        # If this is a new record, save it first to get the record_id
        if not self.record_id:
            super().save(*args, **kwargs)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Delete the attachment file when the record is deleted
        if self.attachments:
            if os.path.isfile(self.attachments.path):
                os.remove(self.attachments.path)
        super().delete(*args, **kwargs)

class DoctorAnnotation(models.Model):
    record = models.ForeignKey(
        HealthRecord,
        on_delete=models.CASCADE,
        related_name='annotations'
    )
    doctor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='annotations',
        limit_choices_to={'role': User.Role.DOCTOR}
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'doctor_annotations'
        verbose_name = 'Doctor Annotation'
        verbose_name_plural = 'Doctor Annotations'
        ordering = ['-created_at']

    def __str__(self):
        return f"Annotation by {self.doctor.username} on {self.record.title}"
