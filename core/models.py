from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import date, time
from django.core.exceptions import ValidationError

# --- User Model ---

class User(AbstractUser):
    class Role(models.TextChoices):
        PATIENT = 'PATIENT', 'Patient'
        DOCTOR = 'DOCTOR', 'Doctor'
        ADMIN = 'ADMIN', 'Admin'

    class DayOfWeek(models.TextChoices):
        MONDAY = 'MONDAY', 'Monday'
        TUESDAY = 'TUESDAY', 'Tuesday'
        WEDNESDAY = 'WEDNESDAY', 'Wednesday'
        THURSDAY = 'THURSDAY', 'Thursday'
        FRIDAY = 'FRIDAY', 'Friday'
        SATURDAY = 'SATURDAY', 'Saturday'
        SUNDAY = 'SUNDAY', 'Sunday'

    class AppointmentStatus(models.TextChoices):
        SCHEDULED = 'SCHEDULED', 'Scheduled'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'
        NO_SHOW = 'NO_SHOW', 'No Show'

    # Basic User Fields
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.PATIENT
    )
    date_of_birth = models.DateField(null=True, blank=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Doctor Calendar Fields (null for patients)
    available_days = models.JSONField(
        null=True, 
        blank=True,
        help_text="List of available days with time slots"
    )
    appointment_duration = models.IntegerField(
        null=True, 
        blank=True,
        help_text="Default appointment duration in minutes"
    )
    max_patients_per_day = models.IntegerField(
        null=True, 
        blank=True,
        help_text="Maximum number of patients per day"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize available_days as empty dict for doctors
        if self.role == self.Role.DOCTOR and self.available_days is None:
            self.available_days = {}

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.username} ({self.role})"

    def clean(self):
        super().clean()
        if self.role == self.Role.DOCTOR:
            if not self.email:
                raise ValidationError({
                    'email': 'Email is required for doctors.'
                })
            if not self.available_days:
                raise ValidationError({
                    'available_days': 'Available days are required for doctors.'
                })
            if not self.appointment_duration:
                raise ValidationError({
                    'appointment_duration': 'Appointment duration is required for doctors.'
                })
            if not self.max_patients_per_day:
                raise ValidationError({
                    'max_patients_per_day': 'Maximum patients per day is required for doctors.'
                })

    def save(self, *args, **kwargs):
        if self.role == self.Role.DOCTOR and not self.available_days:
            self.available_days = {}  # Initialize as empty dict for doctors
        super().save(*args, **kwargs)

    @property
    def is_patient(self):
        return self.role == self.Role.PATIENT

    @property
    def is_doctor(self):
        return self.role == self.Role.DOCTOR

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    def get_availability(self, day):
        """Get availability for a specific day"""
        if not self.is_doctor:
            return None
        if not self.available_days:
            self.available_days = {}
            self.save()
        return self.available_days.get(day)

    def set_availability(self, day, start_time, end_time, is_available=True):
        """Set availability for a specific day"""
        if not self.is_doctor:
            raise ValidationError("Only doctors can set availability")
        
        if not self.available_days:
            self.available_days = {}
        
        self.available_days[day] = {
            'start_time': start_time,
            'end_time': end_time,
            'is_available': is_available
        }
        self.save()

    def get_all_availability(self):
        """Get all availability"""
        if not self.is_doctor:
            return None
        return self.available_days

    @property
    def assigned_patients(self):
        """Get all patients assigned to this doctor through appointments"""
        return User.objects.filter(
            role=User.Role.PATIENT,
            doctor_appointments__doctor=self
        ).distinct()

    @property
    def assigned_doctor(self):
        """Get the doctor assigned to this patient through appointments"""
        if self.role == User.Role.PATIENT:
            return User.objects.filter(
                role=User.Role.DOCTOR,
                doctor_appointments__patient=self
            ).first()
        return None

# --- Notification Model ---

class Notification(models.Model):
    class NotificationType(models.TextChoices):
        PATIENT_ASSIGNED = 'PATIENT_ASSIGNED', 'New Patient Assigned'
        ANNOTATION_ADDED = 'ANNOTATION_ADDED', 'Annotation Added'

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

    @classmethod
    def create_patient_assigned_notification(cls, doctor, patient):
        """Create notification when a new patient is assigned to a doctor"""
        return cls.objects.create(
            recipient=doctor,
            notification_type=cls.NotificationType.PATIENT_ASSIGNED,
            title="New Patient Assignment",
            message=f"You have been assigned a new patient: {patient.get_full_name() or patient.username}"
        )

    @classmethod
    def create_annotation_notification(cls, doctor, patient, record):
        """Create notification when a doctor adds an annotation to a patient's record"""
        return cls.objects

class DoctorAppointment(models.Model):
    doctor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='doctor_appointments',
        limit_choices_to={'role': User.Role.DOCTOR}
    )
    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='patient_appointments',
        limit_choices_to={'role': User.Role.PATIENT}
    )
    appointment_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(
        max_length=20,
        choices=User.AppointmentStatus.choices,
        default=User.AppointmentStatus.SCHEDULED
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'doctor_appointments'
        verbose_name = 'Doctor Appointment'
        verbose_name_plural = 'Doctor Appointments'
        ordering = ['-appointment_date', 'start_time']

    def __str__(self):
        return f"{self.doctor.username} - {self.patient.username} ({self.appointment_date})"

    def clean(self):
        # Check if appointment time is within doctor's available hours
        day_of_week = self.appointment_date.strftime('%A').upper()
        availability = self.doctor.get_availability(day_of_week)
        
        if not availability or not availability['is_available']:
            raise ValidationError('Doctor is not available on this day')
        
        if (self.start_time < availability['start_time'] or 
            self.end_time > availability['end_time']):
            raise ValidationError('Appointment time is outside doctor\'s available hours')

        # Check for overlapping appointments
        overlapping = DoctorAppointment.objects.filter(
            doctor=self.doctor,
            appointment_date=self.appointment_date,
            status__in=[User.AppointmentStatus.SCHEDULED],
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        ).exclude(id=self.id)

        if overlapping.exists():
            raise ValidationError('This time slot overlaps with another appointment')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
