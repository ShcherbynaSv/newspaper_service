from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from catalog.models import Topic, Redactor, Article


def index(request: HttpRequest) -> HttpResponse:
    context = {
        "topics": Topic.objects.all().count(),
        "redactors": Redactor.objects.all().count(),
        "articles": Article.objects.all().count(),
    }
    return render(request, "catalog/index.html", context=context)
