__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2020-2021, Vanessa Sochat"
__license__ = "MPL 2.0"

from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from snakeface.apps.users.models import User

admin.site.register(User, UserAdmin)
