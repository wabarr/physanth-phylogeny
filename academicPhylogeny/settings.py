# Django settings for physanth-phylogeny project.
import os
import platform

import secrets
#this is a file called secrets.py that stores sensitive information and is added to the .gitignore file

PROJECT_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)),"..")

DEBUG = True

TEMPLATE_DEBUG = False

#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
ADMINS = (
    ('Andrew Barr', 'wabarr@gmail.com'),
)


MANAGERS = ADMINS

DEV=True
if DEV:
    db = os.path.abspath(os.path.join(PROJECT_DIR,"django_database.db"))
else:
    db = "/home/wabarr/django_database.db"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': db,
        # The following settings are not used with sqlite3:
        'USER': '',
        'PASSWORD': '',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['.ancienteco.com','.physanthphylogeny.org']

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
if DEV:
    MEDIA_ROOT = os.path.join(PROJECT_DIR, "/media/") #FOR DEV ONLY
else:
    MEDIA_ROOT = "/home/wabarr/webapps/physphylostatic/media/"

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
if DEV:
    STATIC_ROOT = os.path.join(PROJECT_DIR, "DEVSTATIC") #FOR DEV ONLY
else:
    STATIC_ROOT = "/home/wabarr/webapps/physphylostatic/"
# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
if DEV:
    STATIC_URL="/static/"
else:
    STATIC_URL = 'http://www.physanthphylogeny.org/static/'

# Additional locations of static files
STATICFILES_DIRS = (#'/home/wabarr/webapps/htdocs/',
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_DIR,"academicPhylogeny/static"),
    os.path.join(PROJECT_DIR,"ajax_select/static"),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = secrets.SECRET_KEY

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'academicPhylogeny.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'academicPhylogeny.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_DIR, 'base/templates'),
    os.path.join(PROJECT_DIR, 'ajax_select/templates'),
    #os.path.join(PROJECT_DIR,'personalWebsite/templates'),
    #os.path.join(PROJECT_DIR,'academicPhylogeny/templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
    #'physanth-phylogeny',
    #'personalWebsite',
    'academicPhylogeny',
    'adverts',
    #'django.contrib.comments',
    #'tagging',
    #'mptt',
    #'zinnia',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for        
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {                                                                                                                        
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'                         
        }
    },
    'handlers': {            
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',                                                         
            'propagate': True,
        },
    }
}

EMAIL_HOST = 'smtp.webfaction.com'   
EMAIL_HOST_USER = 'wabarr'
EMAIL_HOST_PASSWORD = secrets.EMAIL_HOST_PASSWORD
DEFAULT_FROM_EMAIL = 'mail@wabarr.webfactional.com'
SERVER_EMAIL = 'mail@wabarr.webfactional.com'

#FORCE_SCRIPT_NAME = '/django'


TEMPLATE_CONTEXT_PROCESSORS = (
  'django.contrib.auth.context_processors.auth',
  'django.core.context_processors.i18n',
  'django.core.context_processors.request',
  'django.core.context_processors.media',
  'django.core.context_processors.static',
'django.contrib.messages.context_processors.messages',)
  #'zinnia.context_processors.version',)

LOGIN_URL = "/anonymous/"

AJAX_LOOKUP_CHANNELS = {
    # define a custom lookup channel
    'personLookup'   : ('ajax_select.lookups', 'personLookup')
}