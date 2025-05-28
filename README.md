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

