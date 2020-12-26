__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2020-2021, Vanessa Sochat"
__license__ = "MPL 2.0"

from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.http import HttpResponse, Http404, HttpResponseForbidden, JsonResponse
from django.conf import settings
from django.core.paginator import Paginator
from django.contrib import messages
from django.views import generic

from django.views.decorators.cache import never_cache

from decimal import Decimal
import os
import tempfile

from ratelimit.mixins import RatelimitMixin
from ratelimit.decorators import ratelimit
from snakeface.argparser import SnakefaceParser
from snakeface.settings import cfg
from snakeface.apps.main.models import Collection, Workflow
from snakeface.apps.main.forms import CollectionForm, WorkflowForm
from snakeface.apps.users.decorators import login_is_required
from snakeface.settings import (
    VIEW_RATE_LIMIT as rl_rate,
    VIEW_RATE_LIMIT_BLOCK as rl_block,
)


# Dashboard


@login_is_required
@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def index(request):
    collections = None
    if request.user.is_authenticated:
        collections = Collection.objects.filter(owners=request.user)
    return render(
        request,
        "main/index.html",
        {"collections": collections, "page_title": "Dashboard"},
    )


# Workflows


@login_is_required
@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def edit_workflow(request, wid):

    workflow = get_object_or_404(Workflow, pk=wid)

    # Give a warning if the snakefile doesn't exist
    if not os.path.exists(workflow.snakefile):
        messages.warning(
            request, "Warning: This snakefile doesn't appear to exist anymore."
        )

    # Create and update a parser with the current settings
    parser = SnakefaceParser()
    parser.load(workflow.data)
    return edit_or_update_workflow(
        request, workflow=workflow, collection=workflow.collection, parser=parser
    )


@login_is_required
@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def new_workflow(request, cid):
    parser = SnakefaceParser()
    collection = get_object_or_404(Collection, pk=cid)
    return edit_or_update_workflow(request, collection=collection, parser=parser)


def edit_or_update_workflow(request, collection, parser, workflow=None):
    """A shared function to edit or update an existing workflow."""
    action = "update"
    if not workflow:
        action = "create"

    # Case 1: parse a provided form to update current data
    if request.method == "POST":
        for arg, setting in request.POST.items():
            parser.set(arg, setting)

        if not parser.validate():
            message.error(request, parser.errors)
        else:
            if not workflow:
                workflow = Workflow()
            workflow.data = parser.to_dict()
            workflow.snakefile = parser.snakefile
            workflow.workdir = request.POST.get("workdirs", cfg.WORKDIR)
            workflow.collection = collection
            # Save updates the dag and command
            workflow.save()
            return redirect("main:view_workflow", wid=workflow.id)

    # Case 2: no snakefiles:
    if not parser.snakefiles:
        message = (
            "No Snakefiles were found in any path under %s."
            " You must have one to %s a workflow." % (cfg.WORKDIR, action)
        )
        messages.info(request, message)
        return redirect("main:view_collection", cid=workflow.collection.id)

    # Case 3: Render an empty form with current working directory
    form = WorkflowForm()
    if workflow:
        form = WorkflowForm(workdirs=workflow.workdir)
    return render(
        request,
        "workflows/new.html",
        {
            "groups": parser.groups,
            "page_title": "New Workflow",
            "form": form,
            "collection": collection,
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
@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def view_workflow(request, wid):
    workflow = get_object_or_404(Workflow, pk=wid)
    return render(
        request,
        "workflows/detail.html",
        {
            "workflow": workflow,
            "page_title": "%s: %s" % (workflow.collection.name, workflow.id),
        },
    )


# Collections


@login_is_required
@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def edit_collection(request, cid=None):
    """Create a new collection, or edit an existing one. If a cid is provided,
    the view serves to update an existing collection.
    """
    collection = Collection()
    form = CollectionForm()
    exists = False

    if cid:
        collection = get_object_or_404(Collection, pk=cid)
        exists = True
        if request.user not in collection.owners.all():
            return HttpResponseForbidden()

    # Allow view to be used to also update
    form = CollectionForm(request.POST or None, instance=collection)
    page_title = "Edit collection" if exists else "New collection"

    if request.method == "POST" and form.is_valid():
        collection = form.save()
        collection.owners.add(request.user)
        collection.save()
        message = "Your collection %s has been %s." % (
            collection.name,
            "updated" if exists else "created",
        )
        messages.info(request, message)
        return redirect("main:view_collection", cid=collection.id)

    return render(
        request, "collections/new.html", {"form": form, "page_title": page_title}
    )


@login_is_required
@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def view_collection(request, cid):
    collection = get_object_or_404(Collection, pk=cid)
    return render(
        request,
        "collections/detail.html",
        {"collection": collection, "page_title": collection.name},
    )
