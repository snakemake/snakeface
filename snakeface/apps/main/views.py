__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2020-2021, Vanessa Sochat"
__license__ = "MPL 2.0"

from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.http import HttpResponse, Http404, HttpResponseForbidden
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
from snakeface.apps.main.models import Collection
from snakeface.apps.main.forms import CollectionForm
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
    print(collections)
    return render(request, "main/index.html", {"collections": collections})


# Workflows


@login_is_required
@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def new_workflow(request):
    parser = SnakefaceParser()
    if request.method == "POST":
        for arg, setting in request.POST.items():
            parser.set(arg, setting)

    # TODO, how to save to a model?
    return render(request, "workflows/new.html", {"groups": parser.groups})


# Collections


@login_is_required
@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def new_collection(request, cid=None):
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

    if request.method == "POST" and form.is_valid():
        collection = form.save()
        collection.owners.add(request.user)
        collection.save()
        message = "Your collection %s has been %s." % (
            collection.name,
            "updated" if exists else "created",
        )
        messages.info(request, message % collection.name)
        return redirect("main:view_collection", args=[collection.id])

    return render(
        request, "collections/new.html", {"form": form, "page_title": "New Collection"}
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


@login_is_required
@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def edit_collection(request, cid):

    collection = get_object_or_404(Collection, pk=cid)
    form = CollectionForm(instance=collection)
    return render(
        request, "collections/new.html", {"form": form, "page_title": "Edit Collection"}
    )
