__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2020-2021, Vanessa Sochat"
__license__ = "MPL 2.0"

from django.core.exceptions import FieldError
from django.db.models import Q
from django.db.models.signals import pre_save, post_init
from django.db import models
from django.apps import apps
from django.contrib.humanize.templatetags.humanize import intcomma
from django.urls import reverse
from django.utils.safestring import mark_safe


from django.conf import settings
from django.urls import reverse
from django.db import models
from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.fields import (
    JSONField as DjangoJSONField,
    ArrayField as DjangoArrayField,
)

from snakeface.apps.main.utils import CommandRunner, write_file, get_tmpfile
from snakeface.argparser import SnakefaceParser
from snakeface.settings import cfg
from django.db.models import Field

import itertools
import uuid
import json
import os


PRIVACY_CHOICES = (
    (False, "Public (The workflow collection will be accessible by anyone)"),
    (True, "Private (The workflow collection will be not listed.)"),
)


class JSONField(DjangoJSONField):
    pass


if "sqlite" in settings.DATABASES["default"]["ENGINE"]:

    class JSONField(Field):
        def db_type(self, connection):
            return "text"

        def from_db_value(self, value, expression, connection):
            if value is not None:
                return self.to_python(value)
            return value

        def to_python(self, value):
            if value is not None:
                try:
                    return json.loads(value)
                except (TypeError, ValueError):
                    return value
            return value

        def get_prep_value(self, value):
            if value is not None:
                return str(json.dumps(value))
            return value

        def value_to_string(self, obj):
            return self.value_from_object(obj)


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
    name = models.CharField(max_length=250, unique=True, blank=True, null=True)
    data = JSONField(blank=False, null=False, default="{}")
    dag = models.TextField(blank=True, null=True)
    command = models.TextField(blank=False, null=False)
    snakefile = models.TextField(blank=False, null=False, max_length=250)
    workdir = models.TextField(blank=False, null=False, max_length=250)
    snakemake_id = models.TextField(blank=False, null=False)
    add_date = models.DateTimeField("date published", auto_now_add=True)
    modify_date = models.DateTimeField("date modified", auto_now=True)
    owners = models.ManyToManyField(
        "users.User",
        blank=True,
        default=None,
        related_name="workflow_owners",
        related_query_name="owners",
    )
    contributors = models.ManyToManyField(
        "users.User",
        related_name="workflow_contributors",
        related_query_name="contributor",
        blank=True,
        help_text="users with edit permission to the workflow",
        verbose_name="Contributors",
    )

    def get_absolute_url(self):
        return_cid = self.id
        return reverse("workflow_details", args=[str(return_cid)])

    # By default, collections are public
    private = models.BooleanField(
        choices=PRIVACY_CHOICES,
        default=cfg.PRIVATE_ONLY,
        verbose_name="Accessibility",
    )

    def has_view_permission(self):
        if cfg.NOTEBOOK or cfg.NOTEBOOK_ONLY:
            return True
        return (self.private and self.request.user in self.members) or not self.private

    def update_command(self, command=None, do_save=False):
        """Given a command (or an automated save from the signal) update
        the command for the workflow.
        """
        if command:
            self.command = command
        else:
            parser = SnakefaceParser()
            parser.load(self.data)
            self.command = parser.command
        if do_save:
            self.save()

    def update_dag(self, do_save=False):
        """given a snakefile, run the command to update the dag"""
        if self.snakefile and os.path.exists(self.snakefile):
            runner = CommandRunner()

            # First generate the dag, save to temporary dot file
            runner.run_command(
                ["snakemake", "--dag"], cwd=os.path.dirname(self.snakefile)
            )
            filename = write_file(
                get_tmpfile("snakeface-dag-", ".dot"), "".join(runner.output)
            )

            # Next generate the svg with dot, save to model
            runner.run_command(
                ["dot", "-Tsvg", os.path.basename(filename)],
                cwd=os.path.dirname(filename),
            )
            self.dag = "".join(runner.output)
            os.remove(filename)

            # If running from the post_save signal, would be infinite loop
            if do_save:
                self.save()

    def __str__(self):
        return "[workflow:%s]" % self.name

    def get_label(self):
        return "workflow"

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

    class Meta:
        app_label = "main"


class WorkflowStatus(models.Model):
    """A workflow status is a status message send from running a workflow"""

    # executor = models.TextField(null=False, blank=False)
    add_date = models.DateTimeField("date published", auto_now_add=True)
    modify_date = models.DateTimeField("date modified", auto_now=True)
    msg = JSONField(blank=False, null=False, default="{}")
    workflow = models.ForeignKey(
        "main.Workflow", null=False, blank=False, on_delete=models.CASCADE
    )


class Report(models.Model):
    """A report holds a report for a workflow."""

    workflow_run = models.ForeignKey(
        "main.Workflow", null=False, blank=False, on_delete=models.CASCADE
    )


def update_workflow(sender, instance, **kwargs):
    instance.update_dag()
    instance.update_command()


pre_save.connect(update_workflow, sender=Workflow)
