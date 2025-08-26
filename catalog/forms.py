from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from catalog.models import Redactor


class RedactorCreationForm(UserCreationForm):
    class Meta:
        fields = (UserCreationForm.Meta.fields
                  + (
                      "first_name",
                      "last_name",
                      "email",
                      "years_of_experience")
                  )
        model = Redactor


class RedactorUpdateForm(UserChangeForm):
    password = None

    class Meta:
        model = Redactor
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "years_of_experience",
        )
