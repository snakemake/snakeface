__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2020-2021, Vanessa Sochat"
__license__ = "MPL 2.0"

from django.forms import ModelForm
from snakeface.apps.main.models import Collection, Workflow
from snakeface.apps.main.utils import get_workdir_choices
from django import forms


class CollectionForm(ModelForm):
    class Meta:
        model = Collection
        fields = ["name", "private"]


class WorkflowForm(ModelForm):
    workdirs = forms.ChoiceField(choices=get_workdir_choices())

    class Meta:
        model = Workflow
        fields = ["workdirs"]
