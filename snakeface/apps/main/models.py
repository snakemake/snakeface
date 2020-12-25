__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2020-2021, Vanessa Sochat"
__license__ = "MPL 2.0"

from django.core.exceptions import FieldError
from django.db.models import Q
from django.db import models
from django.apps import apps
from django.contrib.humanize.templatetags.humanize import intcomma
from django.urls import reverse
from django.utils.safestring import mark_safe


from django.conf import settings
from django.urls import reverse
from django.db import models
from django.contrib.postgres.fields import JSONField
from taggit.managers import TaggableManager
from snakeface.settings import cfg

import itertools
import uuid


PRIVACY_CHOICES = (
    (False, "Public (The workflow collection will be accessible by anyone)"),
    (True, "Private (The workflow collection will be not listed.)"),
)


class Workflow(models.Model):
    """A workflow is associated with a specific git repository and one or more
    workflow runs.
    """

    repository = models.CharField(
        max_length=250,
        unique=True,
        blank=False,
        null=False,
    )

    snakefile = models.TextField(blank=False, null=False, max_length=250)
    workdir = models.TextField(blank=False, null=False, max_length=250)
    snakemake_id = models.TextField(blank=False, null=False)
    add_date = models.DateTimeField("date published", auto_now_add=True)
    modify_date = models.DateTimeField("date modified", auto_now=True)
    collection = models.ForeignKey(
        "main.Collection", null=False, blank=False, on_delete=models.CASCADE
    )


class WorkflowRun(models.Model):
    """A workflow run is a result for running a workflow."""

    add_date = models.DateTimeField("date published", auto_now_add=True)
    modify_date = models.DateTimeField("date modified", auto_now=True)
    workflow = models.ForeignKey(
        "main.Workflow", null=False, blank=False, on_delete=models.CASCADE
    )


class Report(models.Model):
    """A report holds a report for a workflow."""

    workflow_run = models.ForeignKey(
        "main.WorkflowRun", null=False, blank=False, on_delete=models.CASCADE
    )


class Collection(models.Model):
    """A collection is a group of workflows owned by one or more users"""

    owners = models.ManyToManyField(
        "users.User",
        blank=True,
        default=None,
        related_name="collection_owners",
        related_query_name="owners",
    )

    contributors = models.ManyToManyField(
        "users.User",
        related_name="collection_contributors",
        related_query_name="contributor",
        blank=True,
        help_text="users with edit permission to the collection",
        verbose_name="Contributors",
    )
    name = models.CharField(
        max_length=250,
        unique=True,
        blank=False,
        null=False,
    )
    add_date = models.DateTimeField("date published", auto_now_add=True)
    modify_date = models.DateTimeField("date modified", auto_now=True)
    # metadata = JSONField(default=dict)
    # tags = TaggableManager()
    # TODO: Add interaction limits

    # By default, collections are public
    private = models.BooleanField(
        choices=PRIVACY_CHOICES,
        default=cfg.PRIVATE_ONLY,
        verbose_name="Accessibility",
    )

    def get_absolute_url(self):
        return_cid = self.id
        return reverse("collection_details", args=[str(return_cid)])

    def __str__(self):
        return "[collection:%s]" % self.name

    def get_label(self):
        return "collection"

    @property
    def members(self):
        return list(itertools.chain(self.owners.all(), self.contributors.all()))

    def has_edit_permission(self):
        """If we are running in a notebook environment, there is just one user
        that has edit access to anything. Otherwise, the user must be an owner
        """
        if cfg.NOTEBOOK or cfg.NOTEBOOK_ONLY:
            return True
        return (
            not self.request.user.is_anonymous
            and self.request.user in self.members
            and self.private
        )

    def has_view_permission(self):
        if cfg.NOTEBOOK or cfg.NOTEBOOK_ONLY:
            return True
        return (self.private and self.request.user in self.members) or not self.private

    class Meta:
        app_label = "main"
