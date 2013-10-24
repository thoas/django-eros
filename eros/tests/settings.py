import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test_db',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

SITE_ID = 1
DEBUG = True

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'eros',
    'eros.tests',
    'django_nose',
]

ROOT_URLCONF = 'eros.tests.urls'

TEST_RUNNER = 'discover_runner.DiscoverRunner'

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), 'templates')
)

SECRET_KEY = 'blabla'
