"""
Tests for healthrecords models.
"""
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'healthrecords.tests.test_settings'

from django.test import TestCase
from django.contrib.auth import get_user_model
from healthrecords.tests.setup_test_db import setup_test_db

class HealthRecordModelTests(TestCase):
    """Test cases for HealthRecord model."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database."""
        super().setUpClass()
        setup_test_db()
    
    def setUp(self):
        """Set up test data."""
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_health_record_creation(self):
        """Test health record creation."""
        # Add your test cases here
        pass 