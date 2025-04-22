FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Verify that Python is installed (optional for debugging)
RUN python3 --version

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies from requirements.txt
COPY requirements.txt .  
RUN pip install --upgrade pip && pip install -r requirements.txt

# Optional: If you have a separate test_requirements.txt file, copy and install it
# COPY test_requirements.txt .
# RUN pip install --upgrade pip && pip install -r test_requirements.txt

# Copy the rest of the project files
COPY . .  

# Expose port 8000 for the Django app
EXPOSE 8000

# Default command to run the Django application with Gunicorn
CMD ["gunicorn", "voting_system.wsgi:application", "--bind", "0.0.0.0:8000"]
