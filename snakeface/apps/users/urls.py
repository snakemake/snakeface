# Copyright (C) 2020 Vanessa Sochat.

# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.


from django.conf.urls import url, include
from snakeface.apps.users import views
from social_django import urls as social_urls

urlpatterns = [
    url(r"^login/$", views.login, name="login"),
    url(r"^login/notebook/$", views.notebook_login, name="notebook_login"),
    url(r"^accounts/login/$", views.login),
    url(r"^logout/$", views.logout, name="logout"),
    url("", include(social_urls, namespace="social")),
]

app_name = "users"
