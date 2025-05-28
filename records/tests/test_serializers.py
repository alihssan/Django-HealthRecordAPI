from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from users.models import User
from records.models import HealthRecord, DoctorAnnotation
from records.serializers import HealthRecordSerializer, DoctorAnnotationSerializer
from datetime import date

class HealthRecordSerializerTest(TestCase):
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
        self.health_record.assigned_doctors.add(self.doctor)

    def test_health_record_serialization(self):
        """Test serializing a health record"""
        serializer = HealthRecordSerializer(self.health_record)
        data = serializer.data

        self.assertEqual(data['title'], 'Test Consultation')
        self.assertEqual(data['record_type'], 'CONSULTATION')
        self.assertEqual(data['description'], 'Test consultation record')
        self.assertFalse(data['is_private'])
        self.assertEqual(len(data['assigned_doctors']), 1)
        self.assertEqual(data['assigned_doctors'][0]['username'], 'testdoctor')

    def test_health_record_deserialization(self):
        """Test deserializing and creating a health record"""
        data = {
            'record_type': 'LAB_RESULT',
            'title': 'New Lab Result',
            'description': 'New test result',
            'date': date.today().isoformat(),
            'is_private': True,
            'doctor_ids': [self.doctor.id]
        }
        
        serializer = HealthRecordSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        record = serializer.save(patient=self.patient)
        
        self.assertEqual(record.title, 'New Lab Result')
        self.assertEqual(record.record_type, 'LAB_RESULT')
        self.assertTrue(record.is_private)
        self.assertIn(self.doctor, record.assigned_doctors.all())

    def test_health_record_update(self):
        """Test updating a health record"""
        data = {
            'title': 'Updated Title',
            'description': 'Updated description',
            'is_private': True,
            'doctor_ids': []
        }
        
        serializer = HealthRecordSerializer(self.health_record, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        record = serializer.save()
        
        self.assertEqual(record.title, 'Updated Title')
        self.assertEqual(record.description, 'Updated description')
        self.assertTrue(record.is_private)
        self.assertEqual(record.assigned_doctors.count(), 0)

class DoctorAnnotationSerializerTest(TestCase):
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

    def test_annotation_serialization(self):
        """Test serializing a doctor annotation"""
        serializer = DoctorAnnotationSerializer(self.annotation)
        data = serializer.data

        self.assertEqual(data['content'], 'Test annotation')
        self.assertEqual(data['doctor']['username'], 'testdoctor')
        self.assertEqual(data['doctor']['email'], 'doctor@test.com')

    def test_annotation_deserialization(self):
        """Test deserializing and creating an annotation"""
        data = {
            'content': 'New annotation'
        }
        
        serializer = DoctorAnnotationSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        annotation = serializer.save(record=self.health_record, doctor=self.doctor)
        
        self.assertEqual(annotation.content, 'New annotation')
        self.assertEqual(annotation.doctor, self.doctor)
        self.assertEqual(annotation.record, self.health_record) 