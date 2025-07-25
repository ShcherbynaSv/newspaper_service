from django.urls import path

from catalog.views import (
    index,
    TopicListView,
    RedactorListView,
    ArticleListView
)

urlpatterns = [
    path("", index, name="index"),
    path("topics", TopicListView.as_view(), name="topic-list"),
    path("redactors", RedactorListView.as_view(), name="redactor-list"),
    path("articles", ArticleListView.as_view(), name="article-list"),
]

app_name = "catalog"
