# Use Python image with Alpine for a lightweight base
FROM debian:12

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    binutils \
    gdal-bin \
    libproj-dev \
    libgeos-dev \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy requirements.txt first for Docker cache optimization
COPY requirements.txt .

# Set environment variables
COPY .env .
RUN set -o allexport; source .env; set +o allexport

# Upgrade pip and install Python dependencies with the flag to bypass restrictions
RUN pip3 install --upgrade pip --break-system-packages && pip3 install -r requirements.txt --break-system-packages

# Copy the rest of the Django project files
COPY . .

# Add the wait-for-it.sh script to wait for the Postgres DB to be ready
COPY wait_for_db.sh /wait_for_db.sh
RUN chmod +x /wait_for_db.sh

# Set the default command to run Django
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
