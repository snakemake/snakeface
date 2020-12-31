__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2020-2021, Vanessa Sochat"
__license__ = "MPL 2.0"

from snakeface.settings import cfg
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from snakeface.apps.main.models import Workflow
from snakeface.apps.users.models import User
from snakeface.apps.main.utils import CommandRunner, ThreadRunner

import re

# Notebook run workflow functions


def run_workflow(request, wid, uid):
    """Top level function to ensure that the user has permission to do the run,
    and we direct to the correct function (notebook or not written, another backend)
    """
    workflow = get_object_or_404(Workflow, pk=wid)
    user = get_object_or_404(User, pk=uid)
    running_notebook = cfg.NOTEBOOK or cfg.NOTEBOOK_ONLY

    # Ensure the user has permission to run the workflow
    if user not in workflow.members:
        messages.info(request, "You are not allowed to run this workflow.")

    # The workflow cannot already be running
    elif workflow.status == "RUNNING":
        messages.info(request, "This workflow is already running.")

    elif run_is_allowed(request) and running_notebook:
        workflow.reset()
        t = ThreadRunner(target=doRun, args=[workflow.id, user.id])
        t.setDaemon(True)
        t.set_workflow(workflow)
        t.start()
        workflow.thread = t.thread_id
        workflow.save()
        messages.success(request, "Workflow %s has started running." % workflow.id)
    else:
        messages.info(request, "Snakeface currently only supports notebook runs.")
    return redirect("main:view_workflow", wid=workflow.id)


# Permissions


def run_is_allowed(request):
    """Given a request, check that the run is allowed meaning:
    1. If running a notebook, we aren't over quota for jobs
    2. If not running a notebook, we aren't over user or global limits
    """
    running_notebook = cfg.NOTEBOOK or cfg.NOTEBOOK_ONLY
    running_jobs = Workflow.objects.filter(status="RUNNING").count()
    allowed = True
    if (
        running_notebook
        and cfg.MAXIMUM_NOTEBOOK_JOBS
        and running_jobs >= cfg.MAXIMUM_NOTEBOOK_JOBS
    ):
        messages.info(
            request,
            "You already have the maximum %s jobs running." % cfg.MAXIMUM_NOTEBOOK_JOBS,
        )
        allowed = False

    elif (
        not running_notebook
        and cfg.USER_WORKFLOW_RUNS_LIMIT
        >= Workflow.objects.filter(user=request.user, status="RUNNING").count()
    ):
        messages.info(
            request,
            "You are at your workflow active runs limit. Finish some and try again later.",
        )
        allowed = False

    elif not running_notebook and cfg.USER_WORKFLOW_GLOBAL_RUNS_LIMIT >= running_jobs:
        messages.info(
            request,
            "The server is at the global limit of workflow runs. Try again later.",
        )
        allowed = False

    return allowed


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
        msg = entry.get("msg", "")
        level = levels.get(entry.get("level"), "secondary")
        badge = "<span class='badge badge-%s'>%s</span>" % (
            level,
            entry.get("level", "info"),
        )

        # If it's a traceback, format as code
        if msg and re.search("traceback|exception", msg, re.IGNORECASE):
            msg = "<code>%s</code>" % msg.replace("\n", "<br>")

        entry.update(
            {
                "order": i,
                "job": entry.get("job", ""),
                "msg": msg,
                "level": badge,
            }
        )
        data.append(entry)
    return data


def doRun(wid, uid):
    """The task to run a workflow"""
    workflow = Workflow.objects.get(pk=wid)
    user = User.objects.get(pk=uid)

    runner = CommandRunner()
    workflow.status = "RUNNING"
    workflow.save()

    # Define the function to determine cancelling the run
    def cancel_workflow(wid):
        workflow = Workflow.objects.get(pk=wid)
        return workflow.status == "CANCELLED"

    # Run the command, update when finished
    runner.run_command(
        workflow.command.split(" "),
        env={"WMS_MONITOR_TOKEN": user.token},
        cancel_func=cancel_workflow,
        cancel_func_kwargs={"wid": wid},
    )
    workflow.error = "<br>".join(runner.error)
    workflow.output = "<br>".join(runner.output)
    workflow.status = "NOTRUNNING"
    workflow.retval = runner.retval
    workflow.save()
