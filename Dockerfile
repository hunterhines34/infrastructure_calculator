FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    musl-dev \
    libpq-dev \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create directory for SQLite database
RUN mkdir -p /data/db && \
    chown -R www-data:www-data /data/db

# Create directory for static files
RUN mkdir -p /app/staticfiles && \
    chown -R www-data:www-data /app/staticfiles

# Switch to non-root user
USER www-data

# Command to run on container start
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "calculator.wsgi:application"] 