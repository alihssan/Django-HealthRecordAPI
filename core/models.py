from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import date 

# --- User Model ---

class User(AbstractUser):
    class Role(models.TextChoices):
        PATIENT = 'PATIENT', 'Patient'
        DOCTOR = 'DOCTOR', 'Doctor'
        ADMIN = 'ADMIN', 'Admin'

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.PATIENT
    )
    date_of_birth = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def is_patient(self):
        return self.role == self.Role.PATIENT

    @property
    def is_doctor(self):
        return self.role == self.Role.DOCTOR

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

# --- Notification Model ---

class Notification(models.Model):
    class NotificationType(models.TextChoices):
        DOCTOR_ASSIGNED = 'DOCTOR_ASSIGNED', 'Doctor Assigned'
        RECORD_UPDATED = 'RECORD_UPDATED', 'Record Updated'
        ANNOTATION_ADDED = 'ANNOTATION_ADDED', 'Annotation Added'
        SYSTEM = 'SYSTEM', 'System Notification'

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    related_record = models.ForeignKey(
        'records.HealthRecord', 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications'
    )

    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.notification_type} - {self.recipient.username}"

    def mark_as_read(self):
        self.is_read = True
        self.save(update_fields=['is_read', 'updated_at'])
