# Django Health Records API

A comprehensive healthcare management system built with Django REST Framework, featuring secure patient records management, appointment scheduling, and doctor-patient interactions.

## Features

### Core Features
- 🔐 Secure authentication with JWT tokens
- 👤 Role-based access (Admin/Doctor/Patient)
- 📅 Appointment scheduling system
- 📝 Health record management
- 👨‍⚕️ Doctor availability management
- 💬 Doctor annotations on records
- 📎 File attachments for records
- 🔔 Real-time notifications
- 📱 RESTful API architecture

### Security Features
- JWT-based authentication
- Role-based access control
- Data encryption
- Input validation
- Rate limiting
- CORS protection
- Secure headers

## Tech Stack

### Backend
- Python 3.11.5
- Django 5.2.1
- Django REST Framework
- PostgreSQL
- Redis (for caching)
- Celery (for async tasks)

### Development Tools
- Docker & Docker Compose
- uv (dependency management)
- pytest (testing)
- coverage (test coverage)

## System Architecture

### Components
1. **Authentication Layer**
   - JWT token management
   - Role-based permissions
   - Token refresh mechanism

2. **User Management**
   - Multi-role user system
   - Profile management
   - Doctor scheduling

3. **Appointment System**
   - Booking management
   - Schedule tracking
   - Automatic record creation

4. **Health Records**
   - Multiple record types
   - Doctor annotations
   - File attachments
   - Access control

5. **Notification System**
   - Real-time alerts
   - Email notifications
   - Appointment reminders

### Database Schema

## Prerequisites

- Docker and Docker Compose
- Python 3.11.5 or higher
- uv (for local development)

## Getting Started

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd django-healthrecordapi
   ```

2. Create a `.local.env` file:
   ```bash
   cp .local.env.example .local.env
   ```
   Edit `.local.env` with your configuration.

3. Build and start the containers:
   ```bash
   docker-compose up --build
   ```

4. The API will be available at `http://localhost:8000`

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login and get token
- `POST /api/auth/refresh/` - Refresh access token

### Health Records
- `GET /api/records/` - List health records (filtered by role)
- `POST /api/records/` - Create new health record
- `GET /api/records/{id}/` - Get specific record
- `PUT /api/records/{id}/` - Update record
- `DELETE /api/records/{id}/` - Delete record

### Doctor Operations
- `GET /api/doctors/patients/` - List assigned patients
- `POST /api/doctors/annotations/` - Add annotation to record
- `GET /api/doctors/notifications/` - Get assignment notifications

### Appointment Management
- `POST /api/appointments/book/` - Book appointment
- `GET /api/appointments/available_doctors/` - Get available doctors
- `POST /api/appointments/{id}/cancel/` - Cancel appointment

## Project Structure

```
django-healthrecordapi/
├── healthrecords/          # Main project directory
│   ├── api/               # API endpoints
│   ├── core/              # Core functionality
│   ├── users/             # User management
│   └── notifications/     # Notification system
├── static/                # Static files
├── templates/             # HTML templates
├── tests/                 # Test suite
├── docker-compose.yml     # Docker configuration
├── Dockerfile            # Docker build file
└── pyproject.toml        # Project dependencies
```

## Development

1. Install uv:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Create and activate virtual environment:
   ```bash
   uv venv
   source .venv/bin/activate  # On Unix/macOS
   # or
   .venv\Scripts\activate  # On Windows
   ```

3. Install dependencies:
   ```bash
   uv pip install -r requirements.txt
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```

6. Run development server:
   ```bash
   python manage.py runserver
   ```

## Testing

### Local Testing

```bash
# Run all tests
python manage.py test

# Run specific test module
python manage.py test healthrecords.tests.test_api

# Run specific test class
python manage.py test healthrecords.tests.test_api.TestHealthRecordAPI

# Run specific test method
python manage.py test healthrecords.tests.test_api.TestHealthRecordAPI.test_create_record

# Run tests with coverage report
coverage run manage.py test
coverage report
coverage html  # Generates HTML report in htmlcov/
```

### Docker-based Testing

The project includes a dedicated Docker Compose configuration for testing. This ensures tests run in an isolated environment with a fresh database.

1. Run all tests using Docker:
   ```bash
   ./run_tests.sh
   ```

   Or manually:
   ```bash
   docker compose -f docker-compose.test.yml up --build --abort-on-container-exit
   ```

2. Run specific test modules:
   ```bash
   docker compose -f docker-compose.test.yml run --rm web python manage.py test healthrecords.tests.test_api
   ```

3. Run tests with coverage:
   ```bash
   docker compose -f docker-compose.test.yml run --rm web coverage run manage.py test
   docker compose -f docker-compose.test.yml run --rm web coverage report
   ```

### Test Database

- Tests use a separate PostgreSQL database (healthrecords_test)
- Database is automatically created and destroyed for each test run
- Test data is isolated from development/production data

### Writing Tests

- Place test files in the `tests/` directory
- Follow Django's test naming conventions
- Use Django's TestCase class for database tests
- Use SimpleTestCase for tests that don't need a database
- Use TransactionTestCase for tests that need transaction control

Example test structure:
```python
from django.test import TestCase
from healthrecords.models import HealthRecord

class TestHealthRecordAPI(TestCase):
    def setUp(self):
        # Setup test data
        pass

    def test_create_record(self):
        # Test record creation
        pass

    def test_update_record(self):
        # Test record update
        pass
```

## Running Migrations with Docker Compose

To create and apply database migrations inside your Docker environment, use the following commands:

**Create new migrations (after changing models):**
```bash
docker compose run --rm web python manage.py makemigrations
```

**Apply migrations to the database:**
```bash
docker compose run --rm web python manage.py migrate
```

**Reset database and volumes (if needed):**
```bash
# Stop containers and remove volumes
docker compose down -v

# Rebuild and start containers
docker compose up --build

# Run migrations
docker compose run --rm web python manage.py migrate

# Create superuser
docker compose run --rm web python manage.py createsuperuser
```

> **Tip:**  
> - Replace `web` with the name of your Django service if it's different in your `docker-compose.yml`.
> - Always run these commands from your project root (where `manage.py` and `docker-compose.yml` are located).
> - Use `docker compose down -v` with caution as it will delete all data in your database.

## Additional Services

### Upstash Redis Integration

1. Sign up for Upstash Redis:
   - Go to [Upstash Console](https://console.upstash.com/)
   - Create a new Redis database
   - Copy the REST API URL and token

2. Add Upstash credentials to `.local.env`:
   ```bash
   UPSTASH_REDIS_URL=your_redis_url
   UPSTASH_REDIS_TOKEN=your_redis_token
   ```

3. Install required packages:
   ```bash
   uv pip install django-redis redis
   ```

4. Configure Redis in `settings.py`:
   ```python
   CACHES = {
       "default": {
           "BACKEND": "django_redis.cache.RedisCache",
           "LOCATION": os.getenv("UPSTASH_REDIS_URL"),
           "OPTIONS": {
               "CLIENT_CLASS": "django_redis.client.DefaultClient",
               "PASSWORD": os.getenv("UPSTASH_REDIS_TOKEN"),
           }
       }
   }
   ```

5. Configure Celery for async tasks:
   ```python
   # settings.py
   CELERY_BROKER_URL = os.getenv("UPSTASH_REDIS_URL")
   CELERY_RESULT_BACKEND = os.getenv("UPSTASH_REDIS_URL")
   ```

### Mailjet Integration

1. Sign up for Mailjet:
   - Go to [Mailjet](https://www.mailjet.com/)
   - Create an account and get API credentials

2. Add Mailjet credentials to `.local.env`:
   ```bash
   MAILJET_API_KEY=your_api_key
   MAILJET_API_SECRET=your_api_secret
   MAILJET_SENDER_EMAIL=your_verified_sender_email
   ```

3. Install Mailjet package:
   ```bash
   uv pip install mailjet-rest
   ```

4. Configure email settings in `settings.py`:
   ```python
   EMAIL_BACKEND = 'healthrecords.core.email.MailjetEmailBackend'
   MAILJET_API_KEY = os.getenv('MAILJET_API_KEY')
   MAILJET_API_SECRET = os.getenv('MAILJET_API_SECRET')
   DEFAULT_FROM_EMAIL = os.getenv('MAILJET_SENDER_EMAIL')
   ```

5. Create custom email backend (`healthrecords/core/email.py`):
   ```python
   from django.core.mail.backends.base import BaseEmailBackend
   from mailjet_rest import Client
   import os

   class MailjetEmailBackend(BaseEmailBackend):
       def __init__(self, *args, **kwargs):
           super().__init__(*args, **kwargs)
           self.mailjet = Client(
               auth=(os.getenv('MAILJET_API_KEY'), os.getenv('MAILJET_API_SECRET')),
               version='v3.1'
           )

       def send_messages(self, email_messages):
           for message in email_messages:
               data = {
                   'Messages': [{
                       'From': {'Email': message.from_email},
                       'To': [{'Email': recipient} for recipient in message.to],
                       'Subject': message.subject,
                       'TextPart': message.body,
                   }]
               }
               self.mailjet.send.create(data=data)
   ```

### Async Task Processing

1. Create Celery configuration (`healthrecords/core/celery.py`):
   ```python
   import os
   from celery import Celery

   os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthrecords.settings')

   app = Celery('healthrecords')
   app.config_from_object('django.conf:settings', namespace='CELERY')
   app.autodiscover_tasks()
   ```

2. Add Celery worker to `docker-compose.yml`:
   ```yaml
   services:
     # ... existing services ...
     
     celery:
       build: .
       command: celery -A healthrecords.core.celery worker --loglevel=info
       volumes:
         - .:/app
       env_file:
         - .local.env
       depends_on:
         - web
         - db
   ```

3. Example async task (`healthrecords/notifications/tasks.py`):
   ```python
   from healthrecords.core.celery import app
   from django.core.mail import send_mail

   @app.task
   def send_notification_email(recipient_email, subject, message):
       send_mail(
           subject=subject,
           message=message,
           from_email=None,  # Uses DEFAULT_FROM_EMAIL
           recipient_list=[recipient_email],
           fail_silently=False,
       )
   ```

## API Documentation

### Authentication Endpoints
```
POST /api/auth/register/
  Register new user
  Request:
  {
    "username": "string",
    "email": "string",
    "password": "string",
    "role": "PATIENT|DOCTOR"
  }
  Response: { "user": {...}, "tokens": {...} }

POST /api/auth/login/
  User login
  Request:
  {
    "username": "string",
    "password": "string"
  }
  Response: { "access": "string", "refresh": "string" }

POST /api/auth/refresh/
  Refresh token
  Request: { "refresh": "string" }
  Response: { "access": "string" }
```

### User Management
```
GET /api/users/me/
  Get current user profile
  Response: { "user": {...} }

PUT /api/users/me/
  Update profile
  Request: { "first_name": "string", ... }
  Response: { "user": {...} }

GET /api/users/doctors/
  List doctors (Admin only)
  Response: { "doctors": [...] }

GET /api/users/patients/
  List patients (Admin only)
  Response: { "patients": [...] }
```

### Doctor Operations
```
GET /api/doctors/my_patients/
  Get assigned patients
  Response: { "patients": [...] }

GET /api/doctors/availability/
  Get schedule
  Response: { "availability": {...} }

PUT /api/doctors/availability/
  Update schedule
  Request: { "available_days": {...} }
  Response: { "availability": {...} }
```

### Appointment Management
```
POST /api/appointments/book/
  Book appointment
  Request:
  {
    "doctor_id": "integer",
    "appointment_date": "date",
    "start_time": "time"
  }
  Response: { "appointment": {...}, "health_record": {...} }

GET /api/appointments/available_doctors/
  Get available doctors
  Response: { "doctors": [...] }

POST /api/appointments/{id}/cancel/
  Cancel appointment
  Response: { "appointment": {...} }
```

### Health Records
```
GET /api/records/
  List records
  Response: { "records": [...] }

POST /api/records/
  Create record
  Request:
  {
    "record_type": "string",
    "title": "string",
    "description": "string"
  }
  Response: { "record": {...} }

POST /api/records/{id}/add_annotation/
  Add annotation
  Request: { "content": "string" }
  Response: { "annotation": {...} }
```

## Setup and Installation

### Prerequisites
- Docker and Docker Compose
- Python 3.11.5+
- uv (for local development)

### Environment Setup
1. Clone repository:
   ```bash
   git clone <repository-url>
   cd django-healthrecordapi
   ```

2. Create environment file:
   ```bash
   cp .local.env.example .local.env
   # Edit .local.env with your configuration
   ```

3. Build and start containers:
   ```bash
   docker compose up --build
   ```

### Database Management
```bash
# Create migrations
docker compose run --rm web python manage.py makemigrations

# Apply migrations
docker compose run --rm web python manage.py migrate

# Create superuser
docker compose run --rm web python manage.py createsuperuser
```

### Development Setup
1. Install uv:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Create virtual environment:
   ```bash
   uv venv
   source .venv/bin/activate  # Unix/macOS
   .venv\Scripts\activate     # Windows
   ```

3. Install dependencies:
   ```bash
   uv pip install -r requirements.txt
   ```

## Testing

### Running Tests
```bash
# All tests
python manage.py test

# Specific module
python manage.py test healthrecords.tests.test_api

# With coverage
coverage run manage.py test
coverage report
```

### Docker Testing
```bash
# Run all tests
./run_tests.sh

# Specific tests
docker compose -f docker-compose.test.yml run --rm web python manage.py test healthrecords.tests.test_api
```

## Additional Services

### Redis Integration
1. Configure in `.local.env`:
   ```
   UPSTASH_REDIS_URL=your_redis_url
   UPSTASH_REDIS_TOKEN=your_redis_token
   ```

2. Install packages:
   ```bash
   uv pip install django-redis redis
   ```

### Email Integration
1. Configure in `.local.env`:
   ```
   MAILJET_API_KEY=your_api_key
   MAILJET_API_SECRET=your_api_secret
   MAILJET_SENDER_EMAIL=your_email
   ```

2. Install package:
   ```bash
   uv pip install mailjet-rest
   ```

## Contributing
1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## License
This project is licensed under the MIT License - see the LICENSE file for details.