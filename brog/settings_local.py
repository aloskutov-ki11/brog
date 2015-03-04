DEBUG = True
TEMPLATE_DEBUG = DEBUG

SITE_ID = 1

DATABASES = {
    'default': {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': 'brog',
    'USER': 'postgres',
    'PASSWORD': 'password',
    'HOST': '', # Set to empty string for localhost.
    'PORT': '', # Set to empty string for default.
    }
}

# DATABASES = {
#     'default': {
#     'ENGINE': 'django.db.backends.postgresql_psycopg2',
#     'NAME': 'postgres',
#     'USER': 'postgres',
#     'PASSWORD': 'password',
#     'HOST': '',
#     'PORT': '',
#     }
# }

#MEDIA_ROOT = '/home/andrei/djcode/brog/media'
MEDIA_ROOT = '/home/andrei/uwsgi-tmp/brog/brog/media'
MEDIA_URL = '/media/'

STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'
STATIC_URL = '/static/'
STATIC_ROOT = 'staticfiles'
STATICFILES_DIRS = (
    'brog/static/',
)
