"""
Tests for healthrecords forms.
"""
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'healthrecords.tests.test_settings'

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

class HealthRecordFormTests(TestCase):
    """Test cases for HealthRecord forms."""
    
    def setUp(self):
        """Set up test data."""
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_health_record_form_validation(self):
        """Test health record form validation."""
        # Add your test cases here
        pass
    
    def test_health_record_form_clean(self):
        """Test health record form clean method."""
        # Add your test cases here
        pass 