from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic

from catalog.forms import (
    RedactorCreationForm,
    RedactorUpdateForm,
    ArticleForm,
    TopicSearchForm,
    ArticleSearchForm,
    RedactorSearchForm
)
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

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(TopicListView, self).get_context_data(**kwargs)
        name = self.request.GET.get("name", "")
        context["search_form"] = TopicSearchForm(initial={"name": name})
        return context

    def get_queryset(self):
        queryset = Topic.objects.all()
        form = TopicSearchForm(self.request.GET)
        if form.is_valid():
            return queryset.filter(name__icontains=form.cleaned_data["name"])
        return queryset


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

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(RedactorListView, self).get_context_data(**kwargs)
        full_name = self.request.GET.get("full_name")
        search_form = RedactorSearchForm(
            initial={"full_name": full_name}
        )
        context["search_form"] = search_form
        return context

    def get_queryset(self):
        queryset = Redactor.objects.all()
        form = RedactorSearchForm(self.request.GET)
        if form.is_valid():
            query = form.cleaned_data.get("full_name")
            if query:
                parts = query.strip().split()
                if len(parts) == 2:
                    first, second = parts
                    queryset = (
                        queryset.filter(
                            first_name__icontains=first,
                            last_name__icontains=second
                        )
                        | queryset.filter(
                            first_name__icontains=second,
                            last_name__icontains=first
                        )
                    )
                else:
                    queryset = (
                        queryset.filter(first_name__icontains=query)
                        | queryset.filter(last_name__icontains=query)
                    )
        return queryset


class RedactorCreateView(LoginRequiredMixin, generic.CreateView):
    model = Redactor
    form_class = RedactorCreationForm
    template_name = "catalog/redactor_form.html"
    success_url = reverse_lazy("catalog:redactor-list")


class RedactorDetailView(generic.DetailView):
    model = Redactor


class RedactorUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Redactor
    form_class = RedactorUpdateForm
    template_name = "catalog/redactor_form.html"

    def get_success_url(self):
        return reverse_lazy(
            "catalog:redactor-detail",
            kwargs={"pk": self.object.pk}
        )


class RedactorDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Redactor
    template_name = "catalog/confirm_delete_redactor.html"
    success_url = reverse_lazy("catalog:redactor-list")


class ArticleListView(generic.ListView):
    model = Article
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.prefetch_related("topics")

        topic_id = self.request.GET.get("topic")
        self.topic = Topic.objects.filter(id=topic_id).first() \
            if topic_id else None
        if self.topic:
            queryset = queryset.filter(topics=self.topic)

        self.search_form = ArticleSearchForm(
            self.request.GET or None,
            initial={"title": self.request.GET.get("title", "")}
        )
        if self.search_form.is_valid():
            query = self.search_form.cleaned_data.get("title")
            if query:
                queryset = queryset.filter(title__icontains=query)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "selected_topic": self.topic,
            "search_form": self.search_form,
        })
        return context


class ArticleCreateView(LoginRequiredMixin, generic.CreateView):
    model = Article
    form_class = ArticleForm
    template_name = "catalog/article_form.html"
    success_url = reverse_lazy("catalog:article-list")


class ArticleDetailView(generic.DetailView):
    model = Article

    def get_queryset(self):
        return (
            super().get_queryset()
            .prefetch_related("topics", "redactors")
        )


class ArticleUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = "catalog/article_form.html"

    def get_success_url(self):
        return reverse_lazy(
            "catalog:article-detail",
            kwargs={"pk": self.object.pk}
        )


class ArticleDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Article
    template_name = "catalog/confirm_delete_article.html"
    success_url = reverse_lazy("catalog:article-list")
