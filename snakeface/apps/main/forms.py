__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2020-2021, Vanessa Sochat"
__license__ = "MPL 2.0"

from django.forms import ModelForm
from snakeface.apps.main.models import Workflow
from snakeface.apps.main.utils import get_workdir_choices
from django import forms
from snakeface.settings import cfg


class WorkflowForm(ModelForm):
    workdirs = forms.ChoiceField(choices=get_workdir_choices())

    class Meta:
        model = Workflow

        # Notebooks are always implicitly private, there is only one user
        if cfg.NOTEBOOK:
            fields = ["name", "workdirs"]
        else:
            fields = ["name", "workdirs", "private"]
