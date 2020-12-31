__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2020, Vanessa Sochat"
__license__ = "MPL 2.0"


from django.contrib.auth import logout as auth_logout, authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect
from ratelimit.decorators import ratelimit
from snakeface.apps.users.forms import TokenForm
from snakeface.apps.users.decorators import login_is_required

from snakeface.apps.users.utils import get_notebook_token
from snakeface.settings import (
    VIEW_RATE_LIMIT as rl_rate,
    VIEW_RATE_LIMIT_BLOCK as rl_block,
    cfg,
)


@login_is_required
def logout(request):
    """log the user out, either from the notebook or traditional Django auth"""
    auth_logout(request)

    # Notebook: delete both tokens to ensure we generate a new one on logout
    if cfg.NOTEBOOK or cfg.NOTEBOOK_ONLY:
        return redirect("users:notebook_login")

    # A traditional Django authentication is here
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

            # If the form is valid, get/create the user and log in
            if form.cleaned_data["token"] == valid_token:
                user = authenticate(username=cfg.USERNAME, password=valid_token)
                if not user:
                    messages.warning(request, "That token is not valid.")
                else:
                    login(request, user)
                    return redirect("main:dashboard")
            else:
                messages.warning(request, "That token is not valid.")
        else:
            return render(request, "login/notebook.html", {"form": form})

    # If a user is already authenticated, redirect to dashboard
    if request.user.is_authenticated:
        return redirect("main:dashboard")

    # If the token isn't provided, they need to provide it
    return render(request, "login/notebook.html", {"form": form})
