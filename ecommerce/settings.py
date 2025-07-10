"""
Django settings for ecommerce project.
"""

from pathlib import Path
from decouple import config
from django.urls import reverse_lazy

# Base Directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Security
SECRET_KEY = config('SECRET_KEY', default='django-insecure-your-secret-key-here')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = ['*']

# Installed Applications
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # Third-party apps
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'crispy_forms',

    'crispy_bootstrap5',
    'widget_tweaks',

    # Local apps
    'store',
    'cart',
    'orders',
    'accounts',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add WhiteNoise after security middleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

# URL configuration
ROOT_URLCONF = 'ecommerce.urls'

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cart.context_processors.cart',
            ],
        },
    },
]

WSGI_APPLICATION = 'ecommerce.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static & Media files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise configuration for static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default auto field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Authentication Backends
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Site ID for allauth
SITE_ID = 1

# ✅ Updated Allauth configuration (no deprecations)
ACCOUNT_EMAIL_REQUIRED = True  # Require email for signup
ACCOUNT_USERNAME_REQUIRED = False  # Don't require username
ACCOUNT_AUTHENTICATION_METHOD = 'email'  # Login with email only
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'  # Require email confirmation
ACCOUNT_UNIQUE_EMAIL = True  # Ensure email uniqueness
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3  # Email confirmation expires in 3 days
ACCOUNT_EMAIL_CONFIRMATION_HMAC = True  # Use HMAC for email confirmation

# Redirects
LOGIN_URL = reverse_lazy('user:login')  # Your custom login view
LOGIN_REDIRECT_URL = reverse_lazy('user:dashboard')  # After login
ACCOUNT_LOGOUT_REDIRECT_URL = reverse_lazy('user:login')  # After logout

# Email backend for Gmail SMTP (production)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='webblog902@gmail.com')
# EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='your-app-password')
EMAIL_HOST_PASSWORD = 'ercupdkazeiprbzc'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Stripe settings (secure via .env)
STRIPE_PUBLISHABLE_KEY = config('STRIPE_PUBLISHABLE_KEY', default='pk_test_your_stripe_key')
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY', default='sk_test_your_stripe_key')
STRIPE_WEBHOOK_SECRET = config('STRIPE_WEBHOOK_SECRET', default='whsec_your_stripe_webhook_secret')

# Payment settings for Nigeria
PAYMENT_CURRENCY = 'NGN'  # Nigerian Naira
PAYMENT_COUNTRY = 'NG'    # Nigeria



# Cart
CART_SESSION_ID = 'cart'
