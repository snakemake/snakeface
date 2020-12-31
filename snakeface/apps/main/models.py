__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2020-2021, Vanessa Sochat"
__license__ = "MPL 2.0"

from django.db.models.signals import pre_save
from django.db import models

from django.conf import settings
from django.urls import reverse
from django.contrib.postgres.fields import JSONField as DjangoJSONField

from snakeface.apps.main.utils import CommandRunner, write_file, get_tmpfile, read_file
from snakeface.argparser import SnakefaceParser
from snakeface.settings import cfg
from django.db.models import Field

import itertools
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


RUNNING_CHOICES = [
    ("RUNNING", "RUNNING"),
    ("NOTRUNNING", "NOTRUNNING"),
    ("CANCELLED", "CANCELLED"),
]


class Workflow(models.Model):
    """A workflow is associated with a specific git repository and one or more
    workflow runs.
    """

    add_date = models.DateTimeField("date published", auto_now_add=True)
    command = models.TextField(blank=False, null=False)
    data = JSONField(blank=False, null=False, default="{}")
    dag = models.TextField(blank=True, null=True)
    error = models.TextField(blank=True, null=True)
    output = models.TextField(blank=True, null=True)
    modify_date = models.DateTimeField("date modified", auto_now=True)
    name = models.CharField(max_length=250, unique=True, blank=True, null=True)
    snakefile = models.TextField(blank=False, null=False, max_length=250)
    snakemake_id = models.TextField(blank=False, null=False)
    status = models.TextField(
        choices=RUNNING_CHOICES, default="NOTRUNNING", blank=False, null=False
    )
    thread = models.PositiveIntegerField(default=None, blank=True, null=True)
    retval = models.PositiveIntegerField(default=None, blank=True, null=True)
    workdir = models.TextField(blank=False, null=False, max_length=250)

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

    @property
    def message_fields(self):
        fields = set()
        for status in self.workflowstatus_set.all():
            [fields.add(x) for x in status.msg]
        return fields

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
            self.command = parser.command + " --wms-monitor-arg id=%s" % self.id
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

            # If running from a signal, would be infinite loop
            if do_save:
                self.save()

    def __str__(self):
        return "[workflow:%s]" % self.name

    def get_label(self):
        return "workflow"

    @property
    def members(self):
        return list(itertools.chain(self.owners.all(), self.contributors.all()))

    def get_report(self):
        """load the report file, if it exists."""
        report_file = self._get_report_file()
        if report_file:
            return read_file(report_file)

    def reset(self):
        """Empty all run related fields to prepare for a new run."""
        self.output = None
        self.error = None
        self.retval = None
        self.workflowstatus_set.all().delete()
        self.save()

    def has_report(self):
        """returns True if the workflow command has a designated report, and
        the report file exists
        """
        if self._get_report_file():
            return True
        return False

    def _get_report_file(self):
        report_file = self.data.get("report")
        fullpath = None
        if report_file:
            fullpath = os.path.join(self.workdir, report_file)
        return fullpath

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


def update_workflow(sender, instance, **kwargs):
    instance.update_dag()
    instance.update_command()


pre_save.connect(update_workflow, sender=Workflow)
