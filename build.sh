#!/usr/bin/env bash
# Build script for Render deployment

set -o errexit  # Exit on error

echo "Starting build process..."

# Install backend dependencies
echo "Installing Python dependencies..."
cd backend
pip install -r requirements.txt

# Create static files directory
echo "Creating static files directory..."
mkdir -p staticfiles

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --settings=backend.production_settings

# Run migrations
echo "Running database migrations..."
python manage.py migrate --settings=backend.production_settings

echo "Build completed successfully!"