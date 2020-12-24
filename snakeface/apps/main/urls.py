__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2020-2021, Vanessa Sochat"
__license__ = "MPL 2.0"

from django.conf.urls import url
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="dashboard"),
    path("workflows/new/", views.new_workflow, name="new_workflow"),
    path("workflows/command/", views.workflow_command, name="workflow_command"),
    path("collection/new/", views.edit_collection, name="new_collection"),
    path("collection/<int:cid>/", views.view_collection, name="view_collection"),
    path("collection/<int:cid>/edit", views.edit_collection, name="edit_collection"),
]

app_name = "main"