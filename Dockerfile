# Use Playwright's official base image with all dependencies preinstalled
FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

# Set working directory
WORKDIR /app

# Copy app code
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Expose port
EXPOSE 8000

# Run app with Gunicorn
CMD ["gunicorn", "index:app", "--bind", "0.0.0.0:8000"]
