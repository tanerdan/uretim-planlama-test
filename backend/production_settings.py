# Production settings for Render deployment
import os
from .settings import *

# Security settings
DEBUG = False
ALLOWED_HOSTS = [
    'uretim-planlama-backend.onrender.com',
    'uretim-planlama-frontend.onrender.com',
    '.onrender.com'
]

# Basic Auth activation
BASIC_AUTH_ENABLED = True

# Database - PostgreSQL on Render
import dj_database_url
DATABASES = {
    'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
}

# Static files with WhiteNoise
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# CORS settings for production
CORS_ALLOWED_ORIGINS = [
    "https://uretim-planlama-frontend.onrender.com",
]
CORS_ALLOW_CREDENTIALS = True

# Security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}