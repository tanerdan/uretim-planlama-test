#!/usr/bin/env bash
# Build script for Render deployment

set -o errexit  # Exit on error

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Create static files directory
mkdir -p staticfiles

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate --settings=backend.production_settings

echo "Build completed successfully!"