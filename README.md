# Django Health Records API

A secure and efficient API for managing patient health records with role-based access control for doctors and patients.

## Features

- 🔐 Secure token-based authentication with short-lived tokens (5-minute expiry)
- 👤 User registration and role management (Patient/Doctor)
- 📝 Health record management for patients
- 👨‍⚕️ Doctor access to assigned patient records
- 💬 Doctor annotations on patient records
- 🔔 Real-time notifications for doctor assignments
- 🛡️ Strict access control for sensitive health data
- 🏗️ Modern Django REST Framework architecture

## Tech Stack

- Python 3.11.5
- Django 5.2.1
- Django REST Framework
- PostgreSQL
- Docker & Docker Compose
- uv for dependency management

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

## Security Features

- JWT-based authentication with short-lived tokens
- Role-based access control (RBAC)
- Data encryption at rest
- Input validation and sanitization
- Rate limiting
- CORS configuration
- Secure headers

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