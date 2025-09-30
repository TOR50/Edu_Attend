import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'dev-insecure-secret-key')
# Toggle DEBUG via env: set DJANGO_DEBUG=false in production
DEBUG = os.environ.get('DJANGO_DEBUG', 'true').lower() == 'true'

# Allowed hosts can be provided as a comma-separated env var in production
_allowed_hosts_env = os.environ.get('DJANGO_ALLOWED_HOSTS')
ALLOWED_HOSTS = (
    [h.strip() for h in _allowed_hosts_env.split(',') if h.strip()]
    if _allowed_hosts_env else ['127.0.0.1', 'localhost']
)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
# Let Django collect app static files (e.g., core/static) automatically.
# Add project-level static dirs here only if needed, e.g., BASE_DIR / 'static'.
STATICFILES_DIRS: list[str] = []
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'core.User'

LOGIN_REDIRECT_URL = '/accounts/login-success/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

_csrf_origins_env = os.environ.get('DJANGO_CSRF_TRUSTED_ORIGINS')
CSRF_TRUSTED_ORIGINS = (
    [o.strip() for o in _csrf_origins_env.split(',') if o.strip()]
    if _csrf_origins_env else [
        'http://127.0.0.1',
        'http://localhost',
    ]
)
