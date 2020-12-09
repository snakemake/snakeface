__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2020-2021, Vanessa Sochat"
__license__ = "MPL 2.0"

from django.db.models import Q
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, reverse
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
from snakeface.apps.main.forms import CollectionForm
from snakeface.apps.users.decorators import login_is_required
from snakeface.settings import (
    VIEW_RATE_LIMIT as rl_rate,
    VIEW_RATE_LIMIT_BLOCK as rl_block,
)


@login_is_required
@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def new_workflow(request):
    parser = SnakefaceParser()
    if request.method == "POST":
        for arg, setting in request.POST.items():
            parser.set(arg, setting)
    # TODO, how to save to a model?
    return render(request, "workflows/new.html", {"groups": parser.groups})


@login_is_required
@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def new_collection(request):
    form = CollectionForm()
    if request.method == "POST":
        pass
    return render(
        request, "collections/new.html", {"form": form, "page_title": "New Collection"}
    )


@login_is_required
@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def edit_collection(request, cid):

    try:
        collection = Collection.objects.get(pk=cid)
    except Collection.DoesNotExist:
        raise Http404

    form = CollectionForm(instance=collection)
    return render(
        request, "collections/new.html", {"form": form, "page_title": "Edit Collection"}
    )
