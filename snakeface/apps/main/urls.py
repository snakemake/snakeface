__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2020-2021, Vanessa Sochat"
__license__ = "MPL 2.0"

from django.urls import path
from . import views
from . import tasks

urlpatterns = [
    path("", views.index, name="dashboard"),
    path("workflows/run/<int:wid>/<int:uid>", tasks.run_workflow, name="run_workflow"),
    path("workflows/new/", views.new_workflow, name="new_workflow"),
    path("workflows/<int:wid>/", views.view_workflow, name="view_workflow"),
    path("workflows/command/", views.workflow_command, name="workflow_command"),
    path(
        "workflows/<int:wid>/statuses/",
        views.workflow_statuses,
        name="workflow_statuses",
    ),
    path("workflows/<int:wid>/edit/", views.edit_workflow, name="edit_workflow"),
    path(
        "workflows/<int:wid>/report/",
        views.view_workflow_report,
        name="view_workflow_report",
    ),
    path("workflows/<int:wid>/delete/", views.delete_workflow, name="delete_workflow"),
    path("workflows/<int:wid>/cancel/", views.cancel_workflow, name="cancel_workflow"),
]

app_name = "main"
