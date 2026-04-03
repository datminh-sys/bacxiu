import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-wjp...(giữ-key-cũ-của-ông)...'
DEBUG = True # Chỉnh thành False khi chạy ổn định

ALLOWED_HOSTS = ['*']
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'myapp',
    'gdstorage', # Thêm thằng này vào
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Cho static file trên Render
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'myproject.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ====== CẤU HÌNH WHITE NOISE & STATIC ======
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ====== CẤU HÌNH GOOGLE DRIVE 2TB (QUAN TRỌNG) ======
GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE_CONTENTS = os.getenv('GOOGLE_DRIVE_KEY_DATA')
DEFAULT_FILE_STORAGE = 'gdstorage.storage.GoogleDriveStorage'
GOOGLE_DRIVE_STORAGE_MEDIA_ROOT = 'MiniCloud_Data' 
MEDIA_URL = '/media/'

# ====== WHITELIST NGƯỜI DÙNG ======
# Thay bằng các username ông muốn cho phép vào Cloud
CLOUD_WHITELIST = ['admin', 'datminh-sys', 'ban_cua_ong'] 
LOGIN_URL = 'login'
