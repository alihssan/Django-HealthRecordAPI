from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Notification

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'date_of_birth', 'phone_number', 'address', 'location')}),
        (_('Role'), {'fields': ('role',)}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role'),
        }),
    )

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
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser:
            # Remove role field for non-superusers
            if 'role' in form.base_fields:
                del form.base_fields['role']
        return form

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
