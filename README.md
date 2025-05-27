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

```bash
# Run all tests
python manage.py test

# Run specific test
python manage.py test healthrecords.tests.test_api
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, email [support@example.com](mailto:support@example.com) or open an issue in the repository.
