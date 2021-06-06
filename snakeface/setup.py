__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2020-2021, Vanessa Sochat"
__license__ = "MPL 2.0"

import os
import shutil
import yaml
from snakeface.logger import logger
from pathlib import Path
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USER_HOME = os.path.expanduser(os.path.join("~", ".snakeface"))
USER_SETTINGS = os.path.join(USER_HOME, "settings.yml")

STATIC_ROOT = os.path.join(USER_HOME, "static")
MEDIA_ROOT = os.path.join(USER_HOME, "data")
USER_DATABASE = os.path.join(USER_HOME, "db.sqlite3")

MIGRATIONS_MODULE = "snakefacedb"
MIGRATIONS_MODULE_PATH = os.path.join(USER_HOME, MIGRATIONS_MODULE)


# Read in the settings file to get settings
class Settings:
    """convert a dictionary of settings (from yaml) into a class"""

    def __init__(self, settings_file):
        self.settings_file = settings_file
        with open(settings_file, "r") as fd:
            self.load(yaml.load(fd.read(), Loader=yaml.FullLoader))

    def save(self):
        """
        Save the settings file if there are changes
        """
        with open(self.settings_file, "w") as fd:
            yaml.dump(self.__dict__, fd)

    def load(self, dictionary):
        for key, value in dictionary.items():
            setattr(self, key, value)
        setattr(self, "UPDATED_AT", datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"))

    def __str__(self):
        return "[snakeface-settings]"

    def __repr__(self):
        return self.__str__()

    def __getattr__(self, key):
        return self.__dict__.get(key)

    def __iter__(self):
        for key, value in self.__dict__.items():
            yield key, value


def init_settings():
    """
    Create user settings in $HOME if they don't exist.
    """
    settings_file = os.path.join(BASE_DIR, "settings.yml")
    if not os.path.exists(settings_file):
        logger.exit(
            "Global settings file settings.yml is missing in the install directory."
        )
    if not os.path.exists(USER_HOME):
        logger.info("Creating user snakeface home at %s" % USER_HOME)
        os.makedirs(USER_HOME)

    if not os.path.exists(USER_SETTINGS):
        logger.info("Creating user settings at %s" % USER_SETTINGS)
        shutil.copyfile(settings_file, USER_SETTINGS)
    return USER_SETTINGS


def init_home():
    """
    Create snakeface use home
    """
    if not os.path.exists(USER_HOME):
        os.makedirs(USER_HOME)
    for dirname in [STATIC_ROOT, MEDIA_ROOT, MIGRATIONS_MODULE_PATH]:
        if not os.path.exists(dirname):
            os.makedirs(dirname)
    init_file = os.path.join(MIGRATIONS_MODULE_PATH, "__init__.py")
    Path(init_file).touch()


def init_snakeface(notebook=True):
    """
    Create all directories that should hold static and media files
    """
    init_home()
    user_settings = init_settings()

    # If the user requested a notebook, add to settings
    if notebook:
        cfg = Settings(user_settings)
        cfg.NOTEBOOK = True
        cfg.save()
    return user_settings
