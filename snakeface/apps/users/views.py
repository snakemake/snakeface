__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2020, Vanessa Sochat"
__license__ = "MPL 2.0"

from snakeface.apps.users.models import User
from snakeface.apps.users.utils import get_notebook_token
from snakeface.apps.main.models import Collection
from snakeface.settings import (
    VIEW_RATE_LIMIT as rl_rate,
    VIEW_RATE_LIMIT_BLOCK as rl_block,
    cfg,
)

from social_core.backends.github import GithubOAuth2
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models.aggregates import Count
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Q, Sum
from ratelimit.decorators import ratelimit
from rest_framework.authtoken.models import Token

from django.utils import timezone
from django.http import JsonResponse, HttpResponseForbidden
from six.moves.urllib.parse import urljoin
from snakeface.apps.users.forms import TokenForm
from snakeface.apps.users.decorators import login_is_required

import uuid


@login_is_required
def logout(request):
    """log the user out, either from the notebook or traditional Django auth"""
    # Notebook: delete both tokens to ensure we generate a new one on logout
    if cfg.NOTEBOOK or cfg.NOTEBOOK_ONLY:
        for key in ["notebook_token", "notebook_auth"]:
            if key in request.session:
                del request.session[key]
        return redirect("users:notebook_login")

    # A traditional Django authentication is here
    auth_logout(request)
    return redirect("/")


@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def notebook_login(request):
    """Given the user doesn't have a token in the request session, ask for it."""
    # If they came to page directly, we need to generate the token
    valid_token = get_notebook_token(request)
    form = TokenForm()

    # If the user is submitting the form, validate it
    if request.method == "POST":
        form = TokenForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["token"] == valid_token:
                request.session["notebook_auth"] = valid_token
                return redirect("base:index")
            else:
                messages.warning(request, "That token is not valid.")
        else:
            return render(
                request, "login/notebook.html", {"form": form, "include_footer": True}
            )

    # If a token is already defined, just redirect to index
    token = request.session.get("notebook_auth")
    if token and token == valid_token:
        return redirect("base:index")

    # Unlikely to have this case, but add in case
    elif token and token != valid_token:
        print("That token is not valid.")
        messages.warning(request, "That token is not valid.")

    # If the token isn't provided, they need to provide it
    return render(
        request, "login/notebook.html", {"form": form, "include_footer": True}
    )
