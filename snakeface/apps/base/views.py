from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.views.decorators.cache import never_cache

from ratelimit.decorators import ratelimit
from snakeface.apps.users.decorators import login_is_required
from snakeface.settings import (
    VIEW_RATE_LIMIT as rl_rate,
    VIEW_RATE_LIMIT_BLOCK as rl_block,
)

# Core Pages


@login_is_required
@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def index(request):
    return render(request, "main/index.html")


# Warmup requests for app engine


def warmup():
    return HttpResponse(status=200)
