from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from catalog.forms import ArticleSearchForm
from catalog.models import Topic, Article


class ArticleListViewTests(TestCase):
    def setUp(self):
        self.url = reverse("catalog:article-list")
        self.topic_1 = Topic.objects.create(name="Culture")
        self.topic_2 = Topic.objects.create(name="Politics")
        self.redactor_1 = get_user_model().objects.create_user(
            first_name="John",
            last_name="Doe",
            username="johndoe",
            password="password1234"
        )
        self.redactor_2 = get_user_model().objects.create_user(
            first_name="Jane",
            last_name="Doe",
            username="janendoe",
            password="password_4321"
        )
        self.article_1 = Article.objects.create(
            title="Test-article-1",
            content="Test-content",
            published_date="2025-10-08",
        )
        self.article_1.topics.add(self.topic_1)
        self.article_1.redactors.add(self.redactor_1)

        self.article_2 = Article.objects.create(
            title="Test-article-2",
            content="Test-content",
            published_date="2025-10-08",
        )
        self.article_2.topics.add(self.topic_2)
        self.article_2.redactors.add(self.redactor_2)

    def test_template_and_context(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/article_list.html")
        self.assertIn("article_list", response.context)
        self.assertIn("search_form", response.context)
        self.assertIn("selected_topic", response.context)

    def test_queryset_no_filter_returns_all(self):
        response = self.client.get(self.url)
        self.assertEqual(
            list(
                response.context["article_list"]),
            [self.article_1, self.article_2]
        )

    def test_filter_by_topic(self):
        response = self.client.get(
            self.url,
            {"topic": self.topic_1.id}
        )
        self.assertIn(self.article_1, response.context["article_list"])
        self.assertNotIn(self.article_2, response.context["article_list"])
        self.assertEqual(
            response.context["selected_topic"],
            self.topic_1
        )

    def test_filter_by_title(self):
        response = self.client.get(self.url, {"title": "-1"})
        self.assertIn(self.article_1, response.context["article_list"])
        self.assertNotIn(self.article_2, response.context["article_list"])
        self.assertIsInstance(
            response.context["search_form"],
            ArticleSearchForm
        )
        self.assertEqual(
            response.context["search_form"].initial.get("title"), "-1"
        )

    def test_combined_filters(self):
        response = self.client.get(
            self.url,
            {
                "topic": self.topic_1.id,
                "title": "-1"
            }
        )
        self.assertIn(self.article_1, response.context["article_list"])
        self.assertNotIn(self.article_2, response.context["article_list"])

    def test_pagination(self):
        [
            Article.objects.create(
                title=f"Title {i}",
                content=f"Content {i}",
                published_date="2025-10-08"
            )
            for i in range(15)
        ]
        response = self.client.get(self.url)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["article_list"]), 10)

        response = self.client.get(self.url, {"page": 2})
        self.assertEqual(len(response.context["article_list"]), 7)

    def test_empty_database(self):
        response = self.client.get(self.url)
        self.assertEqual(
            list(response.context["article_list"]),
            [self.article_1, self.article_2]
        )


class ArticleDetailViewTests(TestCase):
    def setUp(self):
        self.topic = Topic.objects.create(name="Culture")
        self.redactor = get_user_model().objects.create_user(
            username="test-redactor",
            password="Password4321"
        )
        self.article = Article.objects.create(
            title="Test-article-title",
            content="Test-article-content",
            published_date="2025-10-08"
        )
        self.article.topics.add(self.topic)
        self.article.redactors.add(self.redactor)
        self.url = reverse("catalog:article-detail", args=[self.article.id])

    def test_detail_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/article_detail.html")
        self.assertEqual(response.context["article"], self.article)

    def test_context_includes_related_objects(self):
        response = self.client.get(self.url)
        article = response.context["article"]
        self.assertIn(self.topic, article.topics.all())
        self.assertIn(self.redactor, article.redactors.all())

    def test_nonexistent_dish_returns_404(self):
        bad_url = reverse("catalog:article-detail", args=[999])
        response = self.client.get(bad_url)
        self.assertEqual(response.status_code, 404)


class PublicArticleCreateViewTests(TestCase):
    def setUp(self):
        self.url = reverse("catalog:article-create")

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        login_url = reverse("login")
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"{login_url}?next={self.url}")


class PrivateArticleCreateViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="user", password="password123"
        )
        self.client.force_login(self.user)
        self.topic = Topic.objects.create(name="Culture")
        self.url = reverse("catalog:article-create")

    def test_access_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/article_form.html")
        self.assertIn("form", response.context)

    def test_create_valid_article(self):
        data = {
            "title": "Test-article-title",
            "content": "Test-article-content",
            "published_date": "2025-10-08",
            "topics": [self.topic.id],
            "redactors": [self.user.id]
        }
        response = self.client.post(self.url, data)
        article = Article.objects.get(title="Test-article-title")
        self.assertEqual(article.content, "Test-article-content")
        self.assertEqual(article.published_date, date(2025, 10, 8))
        self.assertIn(self.topic, article.topics.all())
        self.assertRedirects(response, reverse("catalog:article-list"))

    def test_create_invalid_article(self):
        response = self.client.post(self.url, {"title": ""})
        self.assertTrue(response.context["form"].errors)
        self.assertEqual(Article.objects.count(), 0)


class PublicArticleUpdateViewTests(TestCase):
    def setUp(self):
        self.topic = Topic.objects.create(name="Culture")
        self.article = Article.objects.create(
            title="Test-article-1",
            content="Test-content",
            published_date="2025-10-08",
        )
        self.article.topics.add(self.topic)
        self.url = reverse("catalog:article-update", args=[self.article.id])

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        login_url = reverse("login")
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"{login_url}?next={self.url}")


class PrivateArticleUpdateViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="user", password="password123"
        )
        self.client.force_login(self.user)

        self.topic = Topic.objects.create(name="Culture")
        self.new_topic = Topic.objects.create(name="Politics")
        self.article = Article.objects.create(
            title="Test-article",
            content="Test-content",
            published_date="2025-10-08",
        )
        self.article.topics.add(self.topic)
        self.url = reverse("catalog:article-update", args=[self.article.id])

    def test_access_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/article_form.html")
        self.assertIn("form", response.context)
        self.assertEqual(
            response.context["form"].initial["title"],
            "Test-article"
        )

    def test_update_valid_article(self):
        data = {
            "title": "New-test-article",
            "content": "Test-article-content",
            "published_date": "2025-10-08",
            "topics": [self.new_topic.id],
            "redactors": [self.user.id],
        }
        response = self.client.post(self.url, data)
        self.article.refresh_from_db()

        self.assertEqual(self.article.title, "New-test-article")
        self.assertEqual(self.article.content, "Test-article-content")
        self.assertEqual(self.article.published_date, date(2025, 10, 8))
        self.assertIn(self.new_topic, self.article.topics.all())
        self.assertRedirects(
            response,
            reverse("catalog:article-detail", args=[self.article.id])
        )

    def test_update_invalid_article(self):
        response = self.client.post(
            self.url,
            {"title": "", }
        )
        form = response.context["form"]
        self.assertTrue(form.errors)
        self.article.refresh_from_db()
        self.assertEqual(self.article.title, "Test-article")

    def test_update_nonexistent_article_returns_404(self):
        bad_url = reverse("catalog:article-update", args=[999])
        response = self.client.get(bad_url)
        self.assertEqual(response.status_code, 404)


class PublicArticleDeleteViewTests(TestCase):
    def setUp(self):
        self.topic = Topic.objects.create(name="Culture")
        self.article = Article.objects.create(
            title="Test-article-1",
            content="Test-content",
            published_date="2025-10-08",
        )
        self.article.topics.add(self.topic)
        self.url = reverse("catalog:article-delete", args=[self.article.id])

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        login_url = reverse("login")
        self.assertRedirects(response, f"{login_url}?next={self.url}")


class PrivateArticleDeleteViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="user", password="password123"
        )
        self.client.force_login(self.user)

        self.topic = Topic.objects.create(name="Culture")
        self.new_topic = Topic.objects.create(name="Politics")
        self.article = Article.objects.create(
            title="Test-article",
            content="Test-content",
            published_date="2025-10-08",
        )
        self.article.topics.add(self.topic)
        self.url = reverse("catalog:article-delete", args=[self.article.id])

    def test_access_delete_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "catalog/confirm_delete_article.html"
        )
        self.assertIn("object", response.context)
        self.assertEqual(response.context["object"], self.article)

    def test_delete_article(self):
        response = self.client.post(self.url)
        self.assertFalse(Article.objects.filter(id=self.article.id).exists())
        self.assertRedirects(response, reverse("catalog:article-list"))

    def test_delete_nonexistent_article_returns_404(self):
        bad_url = reverse("catalog:article-delete", args=[999])
        response = self.client.get(bad_url)
        self.assertEqual(response.status_code, 404)
