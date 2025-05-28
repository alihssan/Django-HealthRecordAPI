from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User
from records.models import HealthRecord, DoctorAnnotation
from datetime import date

class HealthRecordViewTest(TestCase):
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

        # Set up API client
        self.client = APIClient()

    def test_list_records_patient(self):
        """Test listing health records as a patient"""
        self.client.force_authenticate(user=self.patient)
        url = reverse('health-record-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Test Consultation')

    def test_list_records_doctor(self):
        """Test listing health records as a doctor"""
        self.client.force_authenticate(user=self.doctor)
        url = reverse('health-record-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Test Consultation')

    def test_create_record(self):
        """Test creating a new health record"""
        self.client.force_authenticate(user=self.patient)
        url = reverse('health-record-list')
        data = {
            'record_type': 'LAB_RESULT',
            'title': 'New Lab Result',
            'description': 'New test result',
            'date': date.today().isoformat(),
            'is_private': True,
            'doctor_ids': [self.doctor.id]
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(HealthRecord.objects.count(), 2)
        self.assertEqual(response.data['title'], 'New Lab Result')

    def test_update_record(self):
        """Test updating a health record"""
        self.client.force_authenticate(user=self.patient)
        url = reverse('health-record-detail', args=[self.health_record.id])
        data = {
            'title': 'Updated Title',
            'description': 'Updated description'
        }
        
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.health_record.refresh_from_db()
        self.assertEqual(self.health_record.title, 'Updated Title')

    def test_delete_record(self):
        """Test deleting a health record"""
        self.client.force_authenticate(user=self.patient)
        url = reverse('health-record-detail', args=[self.health_record.id])
        
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(HealthRecord.objects.count(), 0)

class DoctorAnnotationViewTest(TestCase):
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

        # Set up API client
        self.client = APIClient()

    def test_create_annotation(self):
        """Test creating a new annotation"""
        self.client.force_authenticate(user=self.doctor)
        url = reverse('doctor-annotation-list')
        data = {
            'record': self.health_record.id,
            'content': 'New annotation'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DoctorAnnotation.objects.count(), 2)
        self.assertEqual(response.data['content'], 'New annotation')

    def test_list_annotations(self):
        """Test listing annotations for a record"""
        self.client.force_authenticate(user=self.doctor)
        url = reverse('doctor-annotation-list')
        response = self.client.get(url, {'record': self.health_record.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['content'], 'Test annotation')

    def test_update_annotation(self):
        """Test updating an annotation"""
        self.client.force_authenticate(user=self.doctor)
        url = reverse('doctor-annotation-detail', args=[self.annotation.id])
        data = {
            'content': 'Updated annotation'
        }
        
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.annotation.refresh_from_db()
        self.assertEqual(self.annotation.content, 'Updated annotation')

    def test_delete_annotation(self):
        """Test deleting an annotation"""
        self.client.force_authenticate(user=self.doctor)
        url = reverse('doctor-annotation-detail', args=[self.annotation.id])
        
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(DoctorAnnotation.objects.count(), 0) 