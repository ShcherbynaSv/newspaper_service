from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic

from catalog.models import Topic, Redactor, Article


def index(request: HttpRequest) -> HttpResponse:
    context = {
        "topics": Topic.objects.all().count(),
        "redactors": Redactor.objects.all().count(),
        "articles": Article.objects.all().count(),
    }
    return render(request, "catalog/index.html", context=context)


class TopicListView(generic.ListView):
    model = Topic
    paginate_by = 10


class TopicCreateView(LoginRequiredMixin, generic.CreateView):
    model = Topic
    fields = "__all__"
    template_name = "catalog/topic_form.html"
    success_url = reverse_lazy("catalog:topic-list")


class TopicUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Topic
    fields = "__all__"
    template_name = "catalog/topic_form.html"
    success_url = reverse_lazy("catalog:topic-list")


class TopicDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Topic
    template_name = "catalog/confirm_delete_topic.html"
    success_url = reverse_lazy("catalog:topic-list")


class RedactorListView(generic.ListView):
    model = Redactor
    paginate_by = 10


class RedactorDetailView(generic.DetailView):
    model = Redactor


class ArticleListView(generic.ListView):
    model = Article
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.topic = None

        topic_id = self.request.GET.get("topics")
        if topic_id:
            queryset = queryset.filter(topics__id=topic_id)
            try:
                self.topic = Topic.objects.get(id=topic_id)
            except Topic.DoesNotExist:
                self.topic = None

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["selected_topic"] = self.topic
        return context


class ArticleDetailView(generic.DetailView):
    model = Article

    def get_queryset(self):
        return (
            super().get_queryset()
            .prefetch_related("topics", "redactors")
        )
