__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2020-2021, Vanessa Sochat"
__license__ = "MPL 2.0"

from django.conf.urls import url
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="dashboard"),
    path("workflows/new/", views.new_workflow, name="new_workflow"),
    path("workflows/<int:wid>/", views.view_workflow, name="view_workflow"),
    path("workflows/command/", views.workflow_command, name="workflow_command"),
    path(
        "workflows/<int:wid>/edit/",
        views.edit_workflow,
        name="edit_workflow",
    ),
]

app_name = "main"
