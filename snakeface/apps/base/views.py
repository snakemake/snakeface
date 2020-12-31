__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2020, Vanessa Sochat"
__license__ = "MPL 2.0"

from django.http import HttpResponse

# Warmup requests for app engine


def warmup():
    return HttpResponse(status=200)
