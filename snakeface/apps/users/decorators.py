#!/usr/bin/env python

__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2020-2021, Vanessa Sochat"
__license__ = "MPL 2.0"

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.shortcuts import resolve_url, redirect
from snakeface.settings import cfg
from snakeface import settings
from urllib.parse import urlparse


def login_is_required(
    function=None, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME
):
    """
    Decorator to extend login required to also check if a notebook auth is
    desired first.
    """

    def wrap(request, *args, **kwargs):

        # If we are using a notebook, the user is required to login with a token
        if (cfg.NOTEBOOK or cfg.NOTEBOOK_ONLY) and not request.user.is_authenticated:
            return redirect("users:notebook_login")

        # If we have the token in the session
        elif (
            cfg.NOTEBOOK
            or cfg.NOTEBOOK_ONLY
            and request.session.get("notebook_auth")
            == request.session.get("notebook_token")
        ):
            return function(request, *args, **kwargs)

        # If the user is authenticated, return the view right away
        elif request.user.is_authenticated:
            return function(request, *args, **kwargs)

        # Otherwise, prepare login url (from django user_passes_test)
        # https://github.com/django/django/blob/master/django/contrib/auth/decorators.py#L10
        path = request.build_absolute_uri()
        resolved_login_url = resolve_url(login_url or settings.LOGIN_URL)
        login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
        current_scheme, current_netloc = urlparse(path)[:2]
        if (not login_scheme or login_scheme == current_scheme) and (
            not login_netloc or login_netloc == current_netloc
        ):
            path = request.get_full_path()
        from django.contrib.auth.views import redirect_to_login

        return redirect_to_login(path, resolved_login_url, redirect_field_name)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
