# Use Python 3.11.5 slim image as base
FROM python:3.11.5-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=healthrecords.settings \
    PATH="/root/.local/bin:${PATH}"

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    uv --version

# Copy project files
COPY . .

# Install dependencies
RUN uv pip install --system django gunicorn && \
    uv pip install --system -e .

# Create static directories
RUN mkdir -p static staticfiles && \
    chmod -R 755 static staticfiles

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "healthrecords.wsgi:application"] 