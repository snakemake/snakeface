__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2020-2021, Vanessa Sochat"
__license__ = "MPL 2.0"

from django import forms


class TokenForm(forms.Form):
    token = forms.CharField(label="Notebook token", max_length=100)
