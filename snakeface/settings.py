__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2020-2021, Vanessa Sochat"
__license__ = "MPL 2.0"

import os
import tempfile
import yaml
import sys

from django.core.management.utils import get_random_secret_key
from snakeface.apps.users.utils import get_username
from datetime import datetime
from importlib import import_module

# Build paths inside the project with the base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# The snakeface global conflict contains all settings.
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.yml")
if not os.path.exists(SETTINGS_FILE):
    sys.exit("Global settings file settings.yml is missing in the install directory.")


# Read in the settings file to get settings
class Settings:
    """convert a dictionary of settings (from yaml) into a class"""

    def __init__(self, dictionary):
        for key, value in dictionary.items():
            setattr(self, key, value)
        setattr(self, "UPDATED_AT", datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"))

    def __str__(self):
        return "[snakeface-settings]"

    def __repr__(self):
        return self.__str__()

    def __iter__(self):
        for key, value in self.__dict__.items():
            yield key, value


with open(SETTINGS_FILE, "r") as fd:
    cfg = Settings(yaml.load(fd.read(), Loader=yaml.FullLoader))

# For each setting, if it's defined in the environment with SNAKEFACE_ prefix, override
for key, value in cfg:
    envar = os.getenv("SNAKEFACE_%s" % key)
    if envar:
        setattr(cfg, key, envar)

# Secret Key


def generate_secret_key(filename):
    """A helper function to write a randomly generated secret key to file"""
    key = get_random_secret_key()
    with open(filename, "w") as fd:
        fd.writelines("SECRET_KEY = '%s'" % key)


# Generate secret key if doesn't exist, and not defined in environment
SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    try:
        from .secret_key import SECRET_KEY
    except ImportError:
        SETTINGS_DIR = os.path.abspath(os.path.dirname(__file__))
        generate_secret_key(os.path.join(SETTINGS_DIR, "secret_key.py"))
        from .secret_key import SECRET_KEY


# Private only should be a boolean
cfg.PRIVATE_ONLY = cfg.PRIVATE_ONLY is not None

# Set the domain name
DOMAIN_NAME = cfg.DOMAIN_NAME
if cfg.DOMAIN_PORT:
    DOMAIN_NAME = "%s:%s" % (DOMAIN_NAME, cfg.DOMAIN_PORT)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True if os.getenv("DEBUG") != "false" else False

# Derive list of plugins enabled from the environment
PLUGINS_LOOKUP = {
    "ldap_auth": False,
    "pam_auth": False,
    "saml_auth": False,
}
PLUGINS_ENABLED = []
using_auth_backend = False
for key, enabled in PLUGINS_LOOKUP.items():
    plugin_key = "PLUGIN_%s_ENABLED" % key.upper()
    if hasattr(cfg, plugin_key) and getattr(cfg, plugin_key) is not None:

        # Don't enable auth backends if we are using a notebook
        if cfg.NOTEBOOK_ONLY or cfg.NOTEBOOK and "AUTH" in plugin_key:
            continue

        if "AUTH" in plugin_key:
            using_auth_backend = True
        PLUGINS_ENABLED.append(key)

# Does the user want a notebook? Default to this if no auth setup
if not hasattr(cfg, "NOTEBOOK"):
    cfg.NOTEBOOK = True if not using_auth_backend else None

# If the working directory isn't defined, set to pwd
if not hasattr(cfg, "WORKDIR") or not cfg.WORKDIR:
    cfg.WORKDIR = os.getcwd()

# SECURITY WARNING: App Engine's security features ensure that it is safe to
# have ALLOWED_HOSTS = ['*'] when the app is deployed. If you deploy a Django
# app not on App Engine, make sure to set an appropriate host here.
# See https://docs.djangoproject.com/en/2.1/ref/settings/
ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    "channels",
    "snakeface.apps.base",
    "snakeface.apps.api",
    "snakeface.apps.main",
    "snakeface.apps.users",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.humanize",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    "crispy_forms",
    "social_django",
    "django_q",
    "rest_framework",
    "rest_framework.authtoken",
]


CRISPY_TEMPLATE_PACK = "bootstrap4"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Do we want to enable the cache?

if cfg.ENABLE_CACHE:
    MIDDLEWARE += [
        "django.middleware.cache.UpdateCacheMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.cache.FetchFromCacheMiddleware",
    ]

    CACHE_MIDDLEWARE_ALIAS = "default"
    CACHE_MIDDLEWARE_SECONDS = 86400  # one day


# If we are using a notebook, use an in memory channel layer
if cfg.NOTEBOOK:
    CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}


ROOT_URLCONF = "snakeface.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "snakeface.context_processors.globals",
            ],
        },
    },
]

TEMPLATES[0]["OPTIONS"]["debug"] = DEBUG
WSGI_APPLICATION = "snakeface.wsgi.application"
ASGI_APPLICATION = "snakeface.asgi.application"

AUTH_USER_MODEL = "users.User"
SOCIAL_AUTH_USER_MODEL = "users.User"
GRAVATAR_DEFAULT_IMAGE = "retro"


# Cache to tmp
CACHE_LOCATION = os.path.join(tempfile.gettempdir(), "snakeface-cache")
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": CACHE_LOCATION,
    }
}

if not os.path.exists(CACHE_LOCATION):
    os.mkdir(CACHE_LOCATION)


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

# Case 1: we are running locally but want to do migration, etc. (set False to True)
if True and os.getenv("APP_ENGINE_HOST") != None:
    print("Warning: connecting to production database.")

    # Running in development, but want to access the Google Cloud SQL instance in production.
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "USER": os.getenv("APP_ENGINE_USERNAME"),
            "PASSWORD": os.getenv("APP_ENGINE_PASSWORD"),
            "NAME": os.getenv("APP_ENGINE_DATABASE"),
            "HOST": os.getenv("APP_ENGINE_HOST"),  # Set to IP address
            "PORT": "",  # empty string for default.
        }
    }

# Case 2: we are running on app engine
elif os.getenv("APP_ENGINE_CONNECTION_NAME") != None:

    # Ensure debug is absolutely off
    TEMPLATES[0]["OPTIONS"]["debug"] = False
    DEBUG = False

    # Running on production App Engine, so connect to Google Cloud SQL using
    # the unix socket at /cloudsql/<your-cloudsql-connection string>
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "HOST": "/cloudsql/%s" % os.getenv("APP_ENGINE_CONNECTION_NAME"),
            "USER": os.getenv("APP_ENGINE_USERNAME"),
            "PASSWORD": os.getenv("APP_ENGINE_PASSWORD"),
            "NAME": os.getenv("APP_ENGINE_DATABASE"),
        }
    }

# Case 3: Database local development uses DATABASE_* variables
elif os.getenv("DATABASE_HOST") is not None:
    # Make sure to export all of these in your .env file
    DATABASES = {
        "default": {
            "ENGINE": os.environ.get("DATABASE_ENGINE", "django.db.backends.mysql"),
            "HOST": os.environ.get("DATABASE_HOST"),
            "USER": os.environ.get("DATABASE_USER"),
            "PASSWORD": os.environ.get("DATABASE_PASSWORD"),
            "NAME": os.environ.get("DATABASE_NAME"),
        }
    }
else:
    # Use sqlite when testing locally
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
    }


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",  # noqa: 501
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",  # noqa: 501
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",  # noqa: 501
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",  # noqa: 501
    },
]

# Django Q
# workers defaults to multiprocessing CPU count, can be set if neede
# This can be sped up running with another database

Q_CLUSTER = {
    "name": "snakecluster",
    "timeout": 90,
    "retry": 120,
    "queue_limit": 50,
    "bulk": 10,
    "orm": "default",
}


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# TODO: we probably want to put these in one spot relative to user home
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_ROOT = "static"
STATIC_URL = "/static/"
MEDIA_ROOT = "data"
MEDIA_URL = "/data/"

# Rate Limiting

VIEW_RATE_LIMIT = "1000/1d"  # The rate limit for each view, django-ratelimit, "50 per day per ipaddress)
VIEW_RATE_LIMIT_BLOCK = (
    True  # Given that someone goes over, are they blocked for the period?
)

# On any admin or plugin login redirect to standard social-auth entry point for agreement to terms
LOGIN_REDIRECT_URL = "/login"
LOGIN_URL = "/login"

# If we are using a notebook, grab the user that started
cfg.USERNAME = None
if cfg.NOTEBOOK or cfg.NOTEBOOK_ONLY:
    cfg.USERNAME = get_username()

AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend"]

## PLUGINS #####################################################################

# Apply any plugin settings
for plugin in PLUGINS_ENABLED:

    plugin_module = "snakeface.plugins." + plugin
    plugin = import_module(plugin_module)

    # Add the plugin to INSTALLED APPS
    INSTALLED_APPS.append(plugin_module)

    # Add AUTHENTICATION_BACKENDS if defined, for authentication plugins
    if hasattr(plugin, "AUTHENTICATION_BACKENDS"):
        AUTHENTICATION_BACKENDS = (
            AUTHENTICATION_BACKENDS + plugin.AUTHENTICATION_BACKENDS
        )

    # Add custom context processors, if defines for plugin
    if hasattr(plugin, "CONTEXT_PROCESSORS"):
        for context_processor in plugin.CONTEXT_PROCESSORS:
            TEMPLATES[0]["OPTIONS"]["context_processors"].append(context_processor)
