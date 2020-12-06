__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2020, Vanessa Sochat"
__license__ = "MPL 2.0"

from django.conf.urls import url
from django.urls import path
from . import views

urlpatterns = [
    path("workflows/new/", views.new_workflow, name="new_workflow"),
]

app_name = "main"
