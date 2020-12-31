__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2020-2021, Vanessa Sochat"
__license__ = "MPL 2.0"

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib import messages
import os

from ratelimit.decorators import ratelimit
from snakeface.argparser import SnakefaceParser
from snakeface.settings import cfg
from snakeface.apps.main.models import Workflow
from snakeface.apps.main.forms import WorkflowForm
from snakeface.apps.main.tasks import run_workflow, serialize_workflow_statuses
from snakeface.apps.users.decorators import login_is_required
from snakeface.settings import (
    VIEW_RATE_LIMIT as rl_rate,
    VIEW_RATE_LIMIT_BLOCK as rl_block,
)


# Dashboard


@login_is_required
@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def index(request):
    workflows = None
    if request.user.is_authenticated:
        workflows = Workflow.objects.filter(owners=request.user)
    return render(
        request,
        "main/index.html",
        {"workflows": workflows, "page_title": "Dashboard"},
    )


# Workflows


@login_is_required
@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def delete_workflow(request, wid):
    workflow = get_object_or_404(Workflow, pk=wid)

    # Ensure that the user is an owner
    if request.user not in workflow.owners.all():
        return HttpResponseForbidden()
    workflow.delete()
    return redirect("main:dashboard")


@login_is_required
@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def cancel_workflow(request, wid):
    workflow = get_object_or_404(Workflow, pk=wid)

    # Ensure that the user is an owner
    if request.user not in workflow.owners.all():
        return HttpResponseForbidden()
    workflow.status = "CANCELLED"
    workflow.save()
    messages.info(
        request, "Your workflow has been cancelled, and will stop within 10 seconds."
    )
    return redirect("main:view_workflow", wid=workflow.id)


@login_is_required
@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def edit_workflow(request, wid):

    workflow = get_object_or_404(Workflow, pk=wid)

    # Ensure that the user is an owner
    if request.user not in workflow.owners.all():
        return HttpResponseForbidden()

    # Give a warning if the snakefile doesn't exist
    if not os.path.exists(workflow.snakefile):
        messages.warning(
            request, "Warning: This snakefile doesn't appear to exist anymore."
        )

    # Create and update a parser with the current settings
    parser = SnakefaceParser()
    parser.load(workflow.data)
    return edit_or_update_workflow(request, workflow=workflow, parser=parser)


@login_is_required
@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def new_workflow(request):
    parser = SnakefaceParser()
    if request.user.is_authenticated:
        return edit_or_update_workflow(request, parser=parser)
    return HttpResponseForbidden()


def edit_or_update_workflow(request, parser, workflow=None):
    """A shared function to edit or update an existing workflow."""

    # Ensure the user has permission to update
    if workflow:
        existed = True
        action = "update"
        if request.user not in workflow.owners.all():
            return HttpResponseForbidden()
    else:
        workflow = Workflow()
        action = "create"
        existed = False

    form = WorkflowForm(request.POST or None, instance=workflow)

    # Case 1: parse a provided form to update current data
    if request.method == "POST" and form.is_valid():

        for arg, setting in request.POST.items():
            parser.set(arg, setting)

        # Has the user gone over the workflow number limit?
        if (
            Workflow.objects.filter(owners=request.user).count()
            >= cfg.USER_WORKFLOW_LIMIT
        ):
            messages.info(
                request, "You are at the workflow limit of %s" % cfg.USER_WORKFLOW_LIMIT
            )
        elif not parser.validate():
            messages.info(request, parser.errors)
        else:
            print("Creating workflow")
            workflow = form.save()
            workflow.data = parser.to_dict()
            workflow.snakefile = parser.snakefile
            workflow.workdir = request.POST.get("workdirs", cfg.WORKDIR)
            workflow.private = (
                True if cfg.PRIVATE_ONLY else request.POST.get("private", 1) == 1
            )
            workflow.owners.add(request.user)
            # Save updates the dag and command
            workflow.save()
            return run_workflow(request=request, wid=workflow.id, uid=request.user.id)

    # Case 2: no snakefiles:
    if not parser.snakefiles:
        message = (
            "No Snakefiles were found in any path under %s."
            " You must have one to %s a workflow." % (cfg.WORKDIR, action)
        )
        messages.info(request, message)
        return redirect("main:dashboard")

    # Case 3: Render an empty form with current working directory
    if existed:
        form.fields["workdirs"].initial = workflow.workdir
    return render(
        request,
        "workflows/new.html",
        {
            "groups": parser.groups,
            "page_title": "%s Workflow" % action.capitalize(),
            "form": form,
            "workflow_id": getattr(workflow, "id", None),
        },
    )


@login_is_required
@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def workflow_command(request):
    """is called from the browser via POST to update the command"""
    parser = SnakefaceParser()
    if request.method == "POST":
        for arg, setting in request.POST.items():
            parser.set(arg, setting)
        return JsonResponse({"command": parser.command})


@login_is_required
def workflow_statuses(request, wid):
    """return serialized workflow statuses for the details view."""
    workflow = get_object_or_404(Workflow, pk=wid)
    return JsonResponse({"data": serialize_workflow_statuses(workflow)})


@login_is_required
@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def view_workflow(request, wid):

    workflow = get_object_or_404(Workflow, pk=wid)
    return render(
        request,
        "workflows/detail.html",
        {
            "workflow": workflow,
            "page_title": "%s: %s" % (workflow.name or "Workflow", workflow.id),
        },
    )


def view_workflow_report(request, wid):
    """If a workflow generated a report and the report exists, render it to a page"""
    workflow = get_object_or_404(Workflow, pk=wid)
    report = workflow.get_report()
    if not report:
        messages.info(request, "This workflow does not have a report file.")
        redirect("main:view_workflow", wid=workflow.id)
    return render(
        request,
        "workflows/report.html",
        {"workflow": workflow, "page_title": "Report", "report": report},
    )
