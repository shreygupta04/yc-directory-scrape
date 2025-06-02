# Use Playwright's official base image with all dependencies preinstalled
FROM mcr.microsoft.com/playwright/python:v1.52.0-jammy

# Set working directory
WORKDIR /app

# Copy app code
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

RUN playwright install

# Expose port
EXPOSE 8000

ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8

# Run app with Gunicorn
CMD ["gunicorn", "index:app", "--bind", "0.0.0.0:8000", "--workers=1", "--threads=1", "--timeout=300"]

