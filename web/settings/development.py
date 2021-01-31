import os
import web.settings.common_config  as config
import web.settings.secret as secret


SECRET_KEY = secret.SECRET_KEY
ALLOWED_HOSTS = secret.ALLOWED_HOSTS
BASE_DIR = config.BASE_DIR
INSTALLED_APPS = config.INSTALLED_APPS
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
SCHEDULER_CONFIG = config.SCHEDULER_CONFIG
SCHEDULER_AUTOSTART = config.SCHEDULER_AUTOSTART
MIDDLEWARE = config.MIDDLEWARE
ROOT_URLCONF = config.ROOT_URLCONF
TEMPLATES = config.TEMPLATES
WSGI_APPLICATION = 'web.wsgi.application'
AUTH_PASSWORD_VALIDATORS = config.AUTH_PASSWORD_VALIDATORS
LANGUAGE_CODE = config.LANGUAGE_CODE
TIME_ZONE = config.TIME_ZONE
USE_I18N = config.USE_I18N
USE_L10N = config.USE_L10N
USE_TZ = config.USE_TZ
STATIC_URL = config.STATIC_URL
STATIC_ROOT = config.STATIC_ROOT
DATABASES = config.DATABASES

# logging settings used for development 
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
#            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            '()': 'djangocolors_formatter.DjangoColorsFormatter',
            'format': '{levelname} {module} {funcName} : {message}',
            'style': '{',
        },
        'verbose': {
#            'format': '{levelname} {message}',
#            '()': 'djangocolors_formatter.DjangoColorsFormatter',
            'format': '{asctime}-{levelname} {filename} {module} {funcName} : {message}',
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
            'level': 'INFO',
        },
        'homeauto.models': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
        },
        'jobs': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
        },
        'wemo': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
        },
        'hue': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
        },
        'decora': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
        },
        'watchers': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
        },
        'vivint': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
        },
        'carrier': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
        },
        'api_infinitude.pyInfinitude': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
        },
        'api_vivint': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
        },
        'api_decora': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
        },
#        'apscheduler': {
#            'handlers': ['console', 'file'],
#            'level': 'DEBUG',
#            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
#        },
    },
}


# ADMIN REORDER
ADMIN_REORDER = (


    {'app': 'auth', 'models': (
       {'model': 'auth.User', 'label': 'Residents and Guest'},
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
       {'model': 'admin.LogEntry','label': 'Administration Logs'},
    )},

    {'app': 'homeauto', 'label': 'House Configuations', 'models': (
       {'model': 'homeauto.Trigger','label': 'Triggers'},
       {'model': 'homeauto.Action','label': 'Actions'},
       {'model': 'homeauto.Zone','label': 'Zones'},
       {'model': 'homeauto.Account', 'label': 'External Accounts'},
       {'model': 'homeauto.Bridge', 'label': 'Hue Bridges'},
       {'model': 'carrier.System', 'label': 'Carrier Systems'},
       {'model': 'watchers.Directory', 'label': 'Watcher Directories'},
       {'model': 'watchers.CustomEvent', 'label': 'Watcher Events'},
    )},

    {'app': 'homeauto', 'label': 'Device Object Data - Autogenerated', 'models': (
       {'model': 'carrier.Profile', 'label': 'Carrier Profiles'},
       {'model': 'carrier.Activity', 'label': 'Carrier Activities'},
       {'model': 'carrier.Status', 'label': 'Carrier Status'},
       {'model': 'wemo.Device', 'label': 'Wemo Devices'},
       {'model': 'decora.Switch', 'label': 'Decora Devices'},
       {'model': 'hue.Light', 'label': 'Hue Lights'},
       {'model': 'hue.Group', 'label': 'Hue Groups'},
       {'model': 'hue.Scene', 'label': 'Hue Scenes'},
       {'model': 'hue.Sensor', 'label': 'Hue Sensors'},
       {'model': 'hue.Schedule', 'label': 'Hue Schedules'},
       {'model': 'hue.SceneLightstate', 'label': 'Hue Lightstates'},
       {'model': 'vivint.Device', 'label': 'Vivint Devices'},
       {'model': 'vivint.Panel', 'label': 'Vivint Panels'},
    )},
)
