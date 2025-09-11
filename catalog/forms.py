from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from catalog.models import Redactor, Article


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


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = "__all__"
        widgets = {
            "published_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "content": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Enter article content...",
                    "class": "form-control"
                }
            ),
            "topics": forms.CheckboxSelectMultiple(),
            "redactors": forms.CheckboxSelectMultiple(),
        }


class TopicSearchForm(forms.Form):
    name = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(attrs={"placeholder": "Search by topic name"})
    )


class ArticleSearchForm(forms.Form):
    title = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={"placeholder": "Search by article title"}
        )
    )


class RedactorSearchForm(forms.Form):
    full_name = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(attrs={"placeholder": "Search by full name"})
    )
