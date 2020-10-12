
import os
import web.secret as secret

#import logging.config

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = secret.SECRET_KEY

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

#SECURE_HSTS_SECONDS = 300
#SECURE_SSL_REDIRECT = True
#SESSION_COOKIE_SECURE = True
#CSRF_COOKIE_SECURE = True
#SECURE_HSTS_INCLUDE_SUBDOMAINS = True
#SECURE_HSTS_PRELOAD = True

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
#            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            '()': 'djangocolors_formatter.DjangoColorsFormatter',
            'format': '{levelname}:{module}:{funcName}: {message}',
            'style': '{',
        },
        'verbose': {
#            'format': '{levelname} {message}',
#            '()': 'djangocolors_formatter.DjangoColorsFormatter',
            'format': '{asctime}-{levelname}:{filename}:{module}:{funcName}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
           'class': 'logging.StreamHandler',
           'formatter': 'simple',
        },
        'file': {
           'class': 'logging.FileHandler',
           'filename': '/home/ha/web_home_auto/web-home-auto.log',
           'formatter': 'verbose',
        },
    },
    'loggers': {
#        'django': {
#            'handlers': ['console', 'file', 'console'],
#            'level': 'DEBUG',
#        },
        'homeauto.apps': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
        },
        'django.server': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
        },
        'homeauto.house': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
        },
        'homeauto.models': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
        },
        'homeauto.vivint': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
        },
        'homeauto.jobs': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
        },
        'homeauto.wemo': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
        },
        'homeauto.hue': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
        },
        'homeauto.decora': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
        },
        'homeauto.watcher': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
        },
        'homeauto.api_infinitude.pyInfinitude': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
        },
        'homeauto.api_vivint': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
        },
#        'homeauto': {
#            'handlers': ['console', 'file'],
#            'level': 'DEBUG',
#        },
#        'apscheduler': {
#            'handlers': ['console', 'file'],
#            'level': 'DEBUG',
#            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
#        },
    },
}



ALLOWED_HOSTS = secret.ALLOWED_HOSTS


# Application definition

INSTALLED_APPS = [
#    'homeauto.apps.AppAdminConfig',
    'admin_reorder',
    'homeauto.apps.Config',
#    'homeauto.api_decora.decora_wifi',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_apscheduler',
#    'homeauto.apps.AppAdmin',
#    'home_auto.models.Service',
#    'home_auto.models.Person',
#    'homeauto.models.Wemo',
#    'home_auto.models.Device',
]

# This scheduler config will:
# - Store jobs in the project database
# - Execute jobs in threads inside the application process
SCHEDULER_CONFIG = {
    "apscheduler.jobstores.default": {
        "class": "django_apscheduler.jobstores:DjangoJobStore"
    },
    'apscheduler.executors.processpool': {
        "type": "threadpool"
    },
}
SCHEDULER_AUTOSTART = True

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'admin_reorder.middleware.ModelAdminReorder',
]

ROOT_URLCONF = 'web.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ["home_auto/templates/"],
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

WSGI_APPLICATION = 'web.wsgi.application'

# ADMIN REORDER
ADMIN_REORDER = (


    {'app': 'auth', 'models': (
       {'model': 'auth.User', 'label': 'Residents and Guest'},
       'auth.Group',
    )},

    {'app': 'django_apscheduler', 'label': 'Scheduling', 'models': (
       {'model': 'homeauto.Job', 'label': 'Job Configuations'},
       {'model': 'django_apscheduler.DjangoJob', 'label': 'Scheduled Jobs'},
       {'model': 'django_apscheduler.DjangoJobExecution', 'label': 'Execution History'},
    )},

    {'app': 'homeauto', 'label': 'House Objects', 'models': (
       {'model': 'homeauto.Nugget','label': 'Nuggets'},
       {'model': 'homeauto.HouseMotionDetector','label': 'House Motion Detectors'},
       {'model': 'homeauto.HouseLight','label': 'House Lights'},
       {'model': 'homeauto.HouseLock','label': 'House Locks'},
       {'model': 'homeauto.HouseSensor','label': 'House Sensors'},
       {'model': 'homeauto.HouseSchedule','label': 'House Schedules'},
    )},

    {'app': 'homeauto', 'label': 'House Configuations', 'models': (
       {'model': 'homeauto.Trigger','label': 'Triggers'},
       {'model': 'homeauto.Action','label': 'Actions'},
       {'model': 'homeauto.Zone','label': 'Zones'},
       {'model': 'homeauto.Account', 'label': 'External Accounts'},
       {'model': 'homeauto.Bridge', 'label': 'Hue Bridges'},
       {'model': 'homeauto.Infinity', 'label': 'Infinity Systems'},
       {'model': 'homeauto.Directory', 'label': 'Watcher Directories'},
       {'model': 'homeauto.CustomEvent', 'label': 'Watcher Events'},
    )},

    {'app': 'homeauto', 'label': 'Device Object Data - Autogenerated', 'models': (
       {'model': 'homeauto.InfProfile', 'label': 'Infinity Profiles'},
       {'model': 'homeauto.InfActivity', 'label': 'Infinity Activities'},
       {'model': 'homeauto.InfStatus', 'label': 'Infinity Status'},
       {'model': 'homeauto.Wemo', 'label': 'Wemo Devices'},
       {'model': 'homeauto.Switch', 'label': 'Decora Devices'},
       {'model': 'homeauto.Light', 'label': 'Hue Lights'},
       {'model': 'homeauto.Group', 'label': 'Hue Groups'},
       {'model': 'homeauto.Scene', 'label': 'Hue Scenes'},
       {'model': 'homeauto.Sensor', 'label': 'Hue Sensors'},
       {'model': 'homeauto.Schedule', 'label': 'Hue Schedules'},
       {'model': 'homeauto.Device', 'label': 'Vivint Devices'},
       {'model': 'homeauto.Panel', 'label': 'Vivint Panels'},
    )},
)

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
DATABASES = {
    'default': {
        'NAME': 'homeauto',
        'ENGINE': 'django.db.backends.mysql',
        'USER': secret.DB_USER,
        'PASSWORD': secret.DB_PASSWORD,
        'OPTIONS': {
          'autocommit': True,
        },
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
