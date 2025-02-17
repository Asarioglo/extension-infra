# Use Python 3.11 slim image as base
# Slim version contains minimal packages needed to run Python
FROM python:3.11-slim

# Environment variables:
# PYTHONDONTWRITEBYTECODE: Prevents Python from writing .pyc files
# PYTHONUNBUFFERED: Ensures Python output is sent straight to terminal (helps with logging)
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
# Note: We install gcc because some Python packages require compilation
# Note: postgresql-client is optional - only needed if you're using PostgreSQL as your database
# You can remove postgresql-client if you're using a different database like SQLite
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file and install Python dependencies
# We copy this first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
# This is done after installing dependencies so changes to code don't trigger
# re-installation of packages
COPY . .

# Set STATIC_ROOT environment variable for Django static files collection
ENV STATIC_ROOT /app/staticfiles


# Collect static files
# This is a Django command that gathers all static files into a single directory
RUN python manage.py collectstatic --noinput

# Expose port 8000 for the Django application
EXPOSE 8000

# Start the server using gunicorn
# Gunicorn is a production-grade WSGI server for Python web applications
# You can also use: CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"] for development
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "api.wsgi:application"]

