import os
from pathlib import Path

# Try to import decouple for environment variables
try:
    from decouple import config
except ImportError:
    # Fallback function if decouple is not installed
    def config(key, default=None, cast=None):
        value = os.environ.get(key, default)
        if cast and value is not None:
            return cast(value)
        return value

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-replace-this-with-your-secure-secret-key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

# ALLOWED_HOSTS configuration
allowed_hosts_str = config('ALLOWED_HOSTS', default='127.0.0.1,localhost')
if allowed_hosts_str:
    ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_str.split(',') if host.strip()]
else:
    ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# Add the myDevil domain if not in development
if not DEBUG:
    if 'betulait.usermd.net' not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append('betulait.usermd.net')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'crispy_forms',
    'crispy_bootstrap4',
    'cryptography',  # Add cryptography package
    
    # Local apps
    'crm.apps.CrmConfig',  # Use the app config class instead of just the app name
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'crm.middleware.ViewerRestrictMiddleware',
    'crm.middleware.EmailVerificationMiddleware',
    'crm.middleware.TwoFactorMiddleware',  # Add the new 2FA middleware
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'projekt_wdrozeniowy.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'crm.context_processors.view_permissions',  # Add this line
            ],
        },
    },
]

WSGI_APPLICATION = 'projekt_wdrozeniowy.wsgi.application'  # Uncomment this line

# Site URL for email links - get from environment or use default
SITE_URL = config('SITE_URL', default='https://betulait.usermd.net')

# Email settings - read from .env or use default console backend for development
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=False, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='helpdesk@example.com')
TEST_EMAIL_RECIPIENT = config('TEST_EMAIL_RECIPIENT', default='')

# ASGI_APPLICATION = 'projekt_wdrozeniowy.asgi.application'
# CHANNEL_LAYERS = {...}

# Database configuration
# Support both SQLite (development) and MySQL (production)
DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.sqlite3'),
        'NAME': config('DB_NAME', default=BASE_DIR / 'db.sqlite3'),
        'USER': config('DB_USER', default=''),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default=''),
        'PORT': config('DB_PORT', default=''),
        # MySQL specific settings
        'OPTIONS': {},
        'TEST': {
            'NAME': config('DB_TEST_NAME', default=None),
            'CHARSET': config('DB_TEST_CHARSET', default='utf8mb4'),
            'COLLATION': config('DB_TEST_COLLATION', default='utf8mb4_unicode_ci'),
        },
        'CONN_MAX_AGE': config('DB_CONN_MAX_AGE', default=0, cast=int),
    }
}

# Add MySQL specific options if MySQL is being used
if 'mysql' in DATABASES['default']['ENGINE']:
    DATABASES['default']['OPTIONS'] = {
        'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        'connect_timeout': 10,
        'read_timeout': 30,
        'write_timeout': 30,
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Authentication settings
AUTHENTICATION_BACKENDS = [
    'crm.auth_backends.EmailOrUsernameModelBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Messages settings
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'info',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

# Internationalization
LANGUAGE_CODE = 'pl'
TIME_ZONE = 'Europe/Warsaw'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'public', 'static')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'public', 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy Forms
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Login URL
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'

# Encryption settings
FILE_ENCRYPTION_KEY = SECRET_KEY[:32]  # Use part of SECRET_KEY as base for file encryption

# SMTP Configuration (configurable via environment variables)
EMAIL_HOST = config('EMAIL_HOST', default='localhost')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=False, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# Default from email
EMAIL_DISPLAY_NAME = config('EMAIL_DISPLAY_NAME', default='Betula IT - Helpdesk')
DEFAULT_FROM_EMAIL = f'{EMAIL_DISPLAY_NAME} <{config("DEFAULT_FROM_EMAIL", default="noreply@betulait.usermd.net")}>'
SERVER_EMAIL = config('SERVER_EMAIL', default='admin@localhost')

# Password reset settings
PASSWORD_RESET_TIMEOUT = config('PASSWORD_RESET_TIMEOUT', default=86400, cast=int)  # 24 hours

# Email timeout settings
EMAIL_TIMEOUT = config('EMAIL_TIMEOUT', default=10, cast=int)  # 10 seconds timeout

# Test email settings
TEST_EMAIL_RECIPIENT = config('TEST_EMAIL_RECIPIENT', default='')

# Security settings for production
if not DEBUG:
    # HTTPS settings
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_REDIRECT_EXEMPT = []
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    # Session security
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # Additional security headers
    X_FRAME_OPTIONS = 'DENY'

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'sql_formatter': {
            'format': '[SQL] {levelname} {asctime} {message}',
            'style': '{',
        }
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'django.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
        },
        'sql_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'sql.log'),
            'formatter': 'sql_formatter',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'crm': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['sql_file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}

# Only enable email logging in production
if not DEBUG:
    LOGGING['loggers']['django']['handlers'].append('mail_admins')
    LOGGING['loggers']['crm']['handlers'].append('mail_admins')

# Admin emails for error notifications
ADMINS = [
    ('Admin', config('ADMIN_EMAIL', default='admin@localhost')),
]
MANAGERS = ADMINS

# Secret code for wiping activity logs - load from environment variables with fallback
LOG_WIPE_SECRET_CODE = config('LOG_WIPE_SECRET_CODE', default='default-secret-code-change-me')

# Google Authenticator settings
GOOGLE_AUTHENTICATOR = {
    'ISSUER_NAME': 'System Helpdesk',
    'TRUSTED_DEVICE_DAYS': 30,  # Number of days to trust a device
    'RECOVERY_CODE_LENGTH': 20,  # Length of recovery code
}
