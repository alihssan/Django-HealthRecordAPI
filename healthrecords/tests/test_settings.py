"""
Test settings for healthrecords app.
"""
from healthrecords.settings import *
import os

# Set a test secret key
SECRET_KEY = 'django-insecure-test-key-for-testing-purposes-only'

# Allow all hosts for testing
ALLOWED_HOSTS = ['*']

# Use PostgreSQL for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'healthrecords_test'),
        'USER': os.environ.get('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'postgres'),
        'HOST': os.environ.get('POSTGRES_HOST', '0.0.0.0'),
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
        'TEST': {
            'NAME': 'healthrecords_test',
        },
    }
}

# Disable password hashing for faster tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable logging during tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
}

# Use JSON serializer for sessions (more secure than PickleSerializer)
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

# Test runner settings
TEST_RUNNER = 'django.test.runner.DiscoverRunner'
TEST_DATABASE_CHARSET = 'utf8'
TEST_DATABASE_COLLATION = 'utf8_general_ci' 