from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from users.models import User
from records.models import HealthRecord, DoctorAnnotation
from datetime import date

class HealthRecordModelTest(TestCase):
    def setUp(self):
        # Create test users
        self.patient = User.objects.create_user(
            username='testpatient',
            password='testpass123',
            email='patient@test.com',
            first_name='Test',
            last_name='Patient',
            role=User.Role.PATIENT
        )
        
        self.doctor = User.objects.create_user(
            username='testdoctor',
            password='testpass123',
            email='doctor@test.com',
            first_name='Test',
            last_name='Doctor',
            role=User.Role.DOCTOR
        )

        # Create a test health record
        self.health_record = HealthRecord.objects.create(
            patient=self.patient,
            record_type=HealthRecord.RecordType.CONSULTATION,
            title='Test Consultation',
            description='Test consultation record',
            date=date.today(),
            is_private=False
        )

    def test_create_health_record(self):
        """Test creating a health record"""
        self.assertEqual(self.health_record.patient, self.patient)
        self.assertEqual(self.health_record.record_type, HealthRecord.RecordType.CONSULTATION)
        self.assertEqual(self.health_record.title, 'Test Consultation')
        self.assertFalse(self.health_record.is_private)

    def test_assign_doctors(self):
        """Test assigning doctors to a health record"""
        self.health_record.assigned_doctors.add(self.doctor)
        self.assertIn(self.doctor, self.health_record.assigned_doctors.all())

    def test_health_record_str(self):
        """Test the string representation of a health record"""
        expected_str = f"Test Consultation - testpatient"
        self.assertEqual(str(self.health_record), expected_str)

    def test_health_record_ordering(self):
        """Test health records are ordered by date and creation time"""
        # Create another record with same date but later creation time
        later_record = HealthRecord.objects.create(
            patient=self.patient,
            record_type=HealthRecord.RecordType.LAB_RESULT,
            title='Later Record',
            description='Created later',
            date=date.today()
        )
        
        records = HealthRecord.objects.all()
        self.assertEqual(records[0], later_record)  # Should be first due to creation time
        self.assertEqual(records[1], self.health_record)

class DoctorAnnotationModelTest(TestCase):
    def setUp(self):
        # Create test users
        self.patient = User.objects.create_user(
            username='testpatient',
            password='testpass123',
            email='patient@test.com',
            first_name='Test',
            last_name='Patient',
            role=User.Role.PATIENT
        )
        
        self.doctor = User.objects.create_user(
            username='testdoctor',
            password='testpass123',
            email='doctor@test.com',
            first_name='Test',
            last_name='Doctor',
            role=User.Role.DOCTOR
        )

        # Create a test health record
        self.health_record = HealthRecord.objects.create(
            patient=self.patient,
            record_type=HealthRecord.RecordType.CONSULTATION,
            title='Test Consultation',
            description='Test consultation record',
            date=date.today()
        )

        # Create a test annotation
        self.annotation = DoctorAnnotation.objects.create(
            record=self.health_record,
            doctor=self.doctor,
            content='Test annotation'
        )

    def test_create_annotation(self):
        """Test creating a doctor annotation"""
        self.assertEqual(self.annotation.record, self.health_record)
        self.assertEqual(self.annotation.doctor, self.doctor)
        self.assertEqual(self.annotation.content, 'Test annotation')

    def test_annotation_str(self):
        """Test the string representation of an annotation"""
        expected_str = f"Annotation by testdoctor on Test Consultation"
        self.assertEqual(str(self.annotation), expected_str)

    def test_annotation_ordering(self):
        """Test annotations are ordered by creation time"""
        # Create another annotation
        later_annotation = DoctorAnnotation.objects.create(
            record=self.health_record,
            doctor=self.doctor,
            content='Later annotation'
        )
        
        annotations = DoctorAnnotation.objects.all()
        self.assertEqual(annotations[0], later_annotation)  # Should be first due to creation time
        self.assertEqual(annotations[1], self.annotation)

    def test_doctor_role_validation(self):
        """Test that only doctors can create annotations"""
        # Try to create annotation with a patient
        with self.assertRaises(ValidationError):
            DoctorAnnotation.objects.create(
                record=self.health_record,
                doctor=self.patient,  # This should fail as patient is not a doctor
                content='Invalid annotation'
            ) 