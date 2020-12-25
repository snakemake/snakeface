__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2020-2021, Vanessa Sochat"
__license__ = "MPL 2.0"

from django.contrib.sites.shortcuts import get_current_site
from snakeface import settings


def globals(request):
    """Returns a dict of defaults to be used by templates, if configured
    correcty in the settings.py file."""
    return {
        "DOMAIN": settings.cfg.DOMAIN_NAME,
        "NOTEBOOK": settings.cfg.NOTEBOOK,
        "TWITTER_USERNAME": settings.cfg.TWITTER_USERNAME,
        "GITHUB_REPOSITORY": settings.cfg.GITHUB_REPOSITORY,
        "GITHUB_DOCUMENTATION": settings.cfg.GITHUB_DOCUMENTATION,
        "HELP_CONTACT_EMAIL": settings.cfg.HELP_CONTACT_EMAIL,
        "SITE_NAME": get_current_site(request).name,
        "GOOGLE_ANALYTICS_ID": settings.cfg.GOOGLE_ANALYTICS_ID,
        "GOOGLE_ANALYTICS_SITE": settings.cfg.GOOGLE_ANALYTICS_SITE,
    }
