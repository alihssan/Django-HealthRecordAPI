from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from .models import User, Notification, DoctorAppointment
from django.utils.html import format_html
import datetime
class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)
    available_days = forms.JSONField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'first_name', 'last_name', 
                 'phone_number', 'address', 'location', 'date_of_birth',
                 'specialization')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('role') == User.Role.DOCTOR:
            cleaned_data['available_days'] = {}  # Initialize empty dict for doctors
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class DoctorAvailabilityForm(forms.ModelForm):
    # Available days
    monday = forms.BooleanField(required=False, label='Monday')
    tuesday = forms.BooleanField(required=False, label='Tuesday')
    wednesday = forms.BooleanField(required=False, label='Wednesday')
    thursday = forms.BooleanField(required=False, label='Thursday')
    friday = forms.BooleanField(required=False, label='Friday')
    saturday = forms.BooleanField(required=False, label='Saturday')
    sunday = forms.BooleanField(required=False, label='Sunday')

    # Time slots for each day
    monday_start = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'type': 'time'}))
    monday_end = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'type': 'time'}))
    tuesday_start = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'type': 'time'}))
    tuesday_end = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'type': 'time'}))
    wednesday_start = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'type': 'time'}))
    wednesday_end = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'type': 'time'}))
    thursday_start = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'type': 'time'}))
    thursday_end = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'type': 'time'}))
    friday_start = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'type': 'time'}))
    friday_end = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'type': 'time'}))
    saturday_start = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'type': 'time'}))
    saturday_end = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'type': 'time'}))
    sunday_start = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'type': 'time'}))
    sunday_end = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'type': 'time'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 
                 'phone_number', 'address', 'location', 'role',
                 'specialization',
                 'appointment_duration', 'max_patients_per_day',
                 'date_of_birth')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.available_days:
            for day, schedule in self.instance.available_days.items():
                day_lower = day.lower()
                self.fields[day_lower].initial = schedule.get('is_available', False)
                self.fields[f'{day_lower}_start'].initial = schedule.get('start_time')
                self.fields[f'{day_lower}_end'].initial = schedule.get('end_time')

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        
        if role == User.Role.DOCTOR:
            if not cleaned_data.get('specialization'):
                raise forms.ValidationError('Specialization is required for doctors')
            available_days = {}
            days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            
            for day in days:
                if cleaned_data.get(day):
                    start_time = cleaned_data.get(f'{day}_start')
                    end_time = cleaned_data.get(f'{day}_end')
                    
                    if not start_time or not end_time:
                        raise forms.ValidationError(f'Please provide both start and end time for {day.capitalize()}')
                    
                    if start_time >= end_time:
                        raise forms.ValidationError(f'End time must be after start time for {day.capitalize()}')
                    
                    available_days[day.upper()] = {
                        'start_time': start_time.strftime('%H:%M'),
                        'end_time': end_time.strftime('%H:%M'),
                        'is_available': True
                    }
            
            if not available_days:
                raise forms.ValidationError('Please select at least one available day')
            
            self.instance.available_days = available_days
            
            if not cleaned_data.get('appointment_duration'):
                raise forms.ValidationError('Appointment duration is required for doctors')
            
            if not cleaned_data.get('max_patients_per_day'):
                raise forms.ValidationError('Maximum patients per day is required for doctors')

        return cleaned_data

class DoctorAppointmentForm(forms.ModelForm):
    available_slots = forms.ChoiceField(choices=[], required=False)

    class Meta:
        model = DoctorAppointment
        fields = ('doctor', 'patient', 'appointment_date', 'start_time', 'end_time', 'status', 'notes')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'doctor' in self.data:
            doctor_id = self.data.get('doctor')
            appointment_date = self.data.get('appointment_date')
            if doctor_id and appointment_date:
                self.fields['available_slots'].choices = self.get_available_slots(doctor_id, appointment_date)

    def get_available_slots(self, doctor_id, appointment_date):
        from datetime import datetime, timedelta
        import json

        doctor = User.objects.get(id=doctor_id)
        day_of_week = datetime.strptime(appointment_date, '%Y-%m-%d').strftime('%A').upper()
        availability = doctor.get_availability(day_of_week)

        if not availability or not availability.get('is_available'):
            return []

        start_time = datetime.strptime(availability['start_time'], '%H:%M')
        end_time = datetime.strptime(availability['end_time'], '%H:%M')
        duration = doctor.appointment_duration or 30  # Default to 30 minutes

        slots = []
        current_time = start_time
        while current_time + timedelta(minutes=duration) <= end_time:
            slot_end = current_time + timedelta(minutes=duration)
            slot_str = f"{current_time.strftime('%H:%M')} - {slot_end.strftime('%H:%M')}"
            slots.append((slot_str, slot_str))
            current_time = slot_end

        return slots

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get('doctor')
        appointment_date = cleaned_data.get('appointment_date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if doctor and appointment_date and start_time and end_time:
            day_of_week = appointment_date.strftime('%A').upper()
            availability = doctor.get_availability(day_of_week)
            
            if not availability:
                raise forms.ValidationError('Doctor has not set availability for this day')
            
            if not availability.get('is_available', False):
                raise forms.ValidationError('Doctor is not available on this day')
            
            # Convert string times to time objects for comparison
            try:
                doctor_start_time = datetime.strptime(availability['start_time'], '%H:%M').time()
                doctor_end_time = datetime.strptime(availability['end_time'], '%H:%M').time()
                
                if (start_time < doctor_start_time or 
                    end_time > doctor_end_time):
                    raise forms.ValidationError('Appointment time is outside doctor\'s available hours')
            except (ValueError, KeyError) as e:
                raise forms.ValidationError(f'Invalid time format in doctor availability: {str(e)}')

            # Check for overlapping appointments
            overlapping = DoctorAppointment.objects.filter(
                doctor=doctor,
                appointment_date=appointment_date,
                status__in=[User.AppointmentStatus.SCHEDULED],
                start_time__lt=end_time,
                end_time__gt=start_time
            ).exclude(id=self.instance.id if self.instance else None)

            if overlapping.exists():
                raise forms.ValidationError('This time slot overlaps with another appointment')

        return cleaned_data

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = DoctorAvailabilityForm
    list_display = ('username', 'email', 'role', 'specialization', 'is_active', 'date_joined', 'show_availability')
    list_filter = ('role', 'specialization', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'specialization')
    ordering = ('-date_joined',)
    
    add_fieldsets = (
        (None, {
            'fields': ('username', 'password1', 'password2')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email', 'role', 'date_of_birth', 'specialization')
        }),
        ('Contact info', {
            'fields': ('phone_number', 'address', 'location')
        }),
    )
    
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email', 'role', 'date_of_birth')
        }),
        ('Contact info', {
            'fields': ('phone_number', 'address', 'location')
        }),
        ('Doctor Schedule', {
            'fields': (
                'specialization',
                ('monday', 'monday_start', 'monday_end'),
                ('tuesday', 'tuesday_start', 'tuesday_end'),
                ('wednesday', 'wednesday_start', 'wednesday_end'),
                ('thursday', 'thursday_start', 'thursday_end'),
                ('friday', 'friday_start', 'friday_end'),
                ('saturday', 'saturday_start', 'saturday_end'),
                ('sunday', 'sunday_start', 'sunday_end'),
                'appointment_duration',
                'max_patients_per_day'
            ),
            'classes': ('collapse',),
            'description': 'These fields are only required for doctors'
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    def show_availability(self, obj):
        if obj.is_doctor and obj.available_days:
            days = []
            for day, schedule in obj.available_days.items():
                if schedule.get('is_available'):
                    days.append(f"{day}: {schedule['start_time']}-{schedule['end_time']}")
            return format_html('<br>'.join(days))
        return '-'
    show_availability.short_description = 'Availability'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # For doctors, only show their assigned patients
        if request.user.role == User.Role.DOCTOR:
            return qs.filter(assigned_doctor=request.user)
        return qs

    def has_add_permission(self, request):
        # Only superusers can add new users
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        # Superusers can change any user
        if request.user.is_superuser:
            return True
        # Doctors can only change their own profile and their patients' profiles
        if request.user.role == User.Role.DOCTOR:
            if obj is None:
                return True
            return obj == request.user or obj.assigned_doctor == request.user
        # Patients can only change their own profile
        if request.user.role == User.Role.PATIENT:
            return obj == request.user
        return False

    def has_delete_permission(self, request, obj=None):
        # Only superusers can delete users
        return request.user.is_superuser

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:  # This is an add form
            return self.add_form
        return super().get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        if obj.role == User.Role.DOCTOR:
            if not obj.specialization:
                raise forms.ValidationError('Specialization is required for doctors')
            available_days = {}
            days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            
            for day in days:
                if form.cleaned_data.get(day):
                    start_time = form.cleaned_data.get(f'{day}_start')
                    end_time = form.cleaned_data.get(f'{day}_end')
                    
                    available_days[day.upper()] = {
                        'start_time': start_time.strftime('%H:%M'),
                        'end_time': end_time.strftime('%H:%M'),
                        'is_available': True
                    }
            
            obj.available_days = available_days
        
        super().save_model(request, obj, form, change)

    def response_add(self, request, obj, post_url_continue=None):
        if obj.role == User.Role.DOCTOR:
            return self.response_change(request, obj)
        return super().response_add(request, obj, post_url_continue)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'title', 'message')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {
            'fields': ('recipient', 'notification_type', 'title', 'message')
        }),
        ('Status', {
            'fields': ('is_read',)
        }),
        ('Related Record', {
            'fields': ('related_record',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        # Only superusers can add notifications
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        # Only superusers can change notifications
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        # Only superusers can delete notifications
        return request.user.is_superuser

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # For doctors, only show their notifications
        if request.user.role == User.Role.DOCTOR:
            return qs.filter(recipient=request.user)
        # For patients, only show their notifications
        if request.user.role == User.Role.PATIENT:
            return qs.filter(recipient=request.user)
        return qs

@admin.register(DoctorAppointment)
class DoctorAppointmentAdmin(admin.ModelAdmin):
    form = DoctorAppointmentForm
    list_display = ('doctor', 'patient', 'appointment_date', 'start_time', 'status')
    list_filter = ('status', 'appointment_date', 'doctor', 'patient')
    search_fields = ('doctor__username', 'patient__username', 'notes')
    ordering = ('-appointment_date', 'start_time')
    readonly_fields = ('created_at', 'updated_at')

    class Media:
        js = ('admin/js/doctor_appointment.js',)
