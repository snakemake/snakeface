__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2020-2021, Vanessa Sochat"
__license__ = "MPL 2.0"

from snakeface.settings import cfg
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404, reverse
import threading
from snakeface.apps.main.models import Workflow
from snakeface.apps.users.models import User
from snakeface.apps.main.utils import CommandRunner, ThreadRunner

# Notebook run workflow functions


def run_workflow(request, wid, uid):
    """Top level function to ensure that the user has permission to do the run,
    and we direct to the correct function (notebook or not written, another backend)
    """
    workflow = get_object_or_404(Workflow, pk=wid)
    user = get_object_or_404(User, pk=uid)

    # Ensure the user has permission to run the workflow
    if user not in workflow.members:
        messages.error(request, "You are not allowed to run this workflow.")

    # The workflow cannot already be running
    elif workflow.status == "RUNNING":
        messages.error(request, "This workflow is already running.")

    elif cfg.NOTEBOOK or cfg.NOTEBOOK_ONLY:
        run_notebook_workflow(request, wid, uid)
    return redirect("main:view_workflow", wid=workflow.id)


def run_notebook_workflow(request, wid, uid):
    workflow = get_object_or_404(Workflow, pk=wid)
    user = get_object_or_404(User, pk=uid)

    # Ensure that we aren't over count
    if (
        cfg.MAXIMUM_NOTEBOOK_JOBS
        and Workflow.objects.filter(status="RUNNING").count()
        >= cfg.MAXIMUM_NOTEBOOK_JOBS
    ):
        messages.info(
            request,
            "You already have the maximum %s jobs running." % cfg.MAXIMUM_NOTEBOOK_JOBS,
        )
    else:
        t = ThreadRunner(target=doRun, args=[workflow.id, user.id])
        t.setDaemon(True)
        t.set_workflow(workflow)
        t.start()
        messages.success(request, "Workflow %s has started running." % workflow.id)


# Statuses


def serialize_workflow_statuses(workflow):
    """A shared helper function to serialize a list of workflow statuses into
    json.
    """
    levels = {
        "debug": "primary",
        "dag_debug": "primary",
        "info": "info",
        "warning": "warning",
        "error": "danger",
    }
    data = []
    for i, status in enumerate(workflow.workflowstatus_set.all()):
        entry = status.msg
        level = levels.get(entry.get("level"), "secondary")
        badge = "<span class='badge badge-%s'>%s</span>" % (
            level,
            entry.get("level", "info"),
        )
        entry.update(
            {
                "order": i,
                "job": entry.get("job", ""),
                "msg": entry.get("msg", ""),
                "level": badge,
            }
        )
        data.append(entry)
    return data


def checkRun(request, wid):
    workflow = Workflow.objects.get(pk=wid)
    return JsonResponse({"status": workflow.status})


def doRun(wid, uid):
    """The task to run a workflow"""
    workflow = Workflow.objects.get(pk=wid)
    user = User.objects.get(pk=uid)

    # Clear the workflow of old output, return codes, and errors
    workflow.output = None
    workflow.error = None
    workflow.retval = None
    workflow.workflowstatus_set.all().delete()

    runner = CommandRunner()
    workflow.status = "RUNNING"
    workflow.save()

    # Run the command, update when finished
    runner.run_command(
        workflow.command.split(" "), env={"WMS_MONITOR_TOKEN": user.token}
    )
    workflow.error = "<br>".join(runner.error)
    workflow.output = "<br>".join(runner.output)
    workflow.status = "NOTRUNNING"
    workflow.retval = runner.retval
    workflow.save()
