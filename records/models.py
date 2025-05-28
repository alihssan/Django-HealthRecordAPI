from django.db import models
from core.models import User

class HealthRecord(models.Model):
    class RecordType(models.TextChoices):
        CONSULTATION = 'CONSULTATION', 'Consultation'
        LAB_RESULT = 'LAB_RESULT', 'Lab Result'
        PRESCRIPTION = 'PRESCRIPTION', 'Prescription'
        VACCINATION = 'VACCINATION', 'Vaccination'
        OTHER = 'OTHER', 'Other'

    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='health_records',
        limit_choices_to={'role': User.Role.PATIENT}
    )
    assigned_doctors = models.ManyToManyField(
        User,
        related_name='assigned_records',
        limit_choices_to={'role': User.Role.DOCTOR},
        blank=True
    )
    record_type = models.CharField(
        max_length=20,
        choices=RecordType.choices,
        default=RecordType.CONSULTATION
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_private = models.BooleanField(default=False)
    attachments = models.FileField(upload_to='health_records/', blank=True, null=True)

    class Meta:
        db_table = 'health_records'
        verbose_name = 'Health Record'
        verbose_name_plural = 'Health Records'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.title} - {self.patient.username}"

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
