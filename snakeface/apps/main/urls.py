__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2020-2021, Vanessa Sochat"
__license__ = "MPL 2.0"

from django.conf.urls import url
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="dashboard"),
    path("workflows/<int:cid>/new/", views.new_workflow, name="new_workflow"),
    path("workflows/command/", views.workflow_command, name="workflow_command"),
    path("collection/new/", views.edit_collection, name="new_collection"),
    path("collection/<int:cid>/", views.view_collection, name="view_collection"),
    path("collection/<int:cid>/edit/", views.edit_collection, name="edit_collection"),
    path(
        "collection/workflows/<int:wid>/edit/",
        views.edit_workflow,
        name="edit_workflow",
    ),
    path("collection/workflows/<int:wid>/", views.view_workflow, name="view_workflow"),
]

app_name = "main"
