from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib import admin
from django.utils import timezone

from catalog.admin import RedactorAdmin, ArticleAdmin
from catalog.models import Redactor, Article


class AdminSiteTests(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            username="admin",
            password="admin1234"
        )
        self.client.force_login(self.admin_user)

        self.redactor = get_user_model().objects.create_user(
            username="test-redactor",
            password="redactor-1234",
            years_of_experience=10
        )
        self.article = Article.objects.create(
            title="test-article",
            content="test-article-content",
            published_date=timezone.now()
        )

    def test_redactor_list_display(self):
        url = reverse("admin:catalog_redactor_changelist")
        res = self.client.get(url)

        self.assertContains(res, str(self.redactor.years_of_experience))

    def test_redactor_list_filter(self):
        model_admin = RedactorAdmin(Redactor, admin.site)
        self.assertEqual(
            model_admin.list_filter,
            (
                "is_staff",
                "is_superuser",
                "is_active",
                "groups",
                "years_of_experience"
            )
        )

    def test_redactor_fieldsets_contains_additional_info(self):
        model_admin = RedactorAdmin(Redactor, admin.site)
        fieldsets = dict(model_admin.fieldsets)
        self.assertIn("Additional info", fieldsets)
        self.assertIn(
            "years_of_experience",
            fieldsets["Additional info"]["fields"]
        )

    def test_redactor_add_fieldsets_contains_additional_info(self):
        model_admin = RedactorAdmin(Redactor, admin.site)
        add_fieldsets = dict(model_admin.add_fieldsets)
        self.assertIn("Additional info", add_fieldsets)
        self.assertIn("first_name", add_fieldsets["Additional info"]["fields"])
        self.assertIn("last_name", add_fieldsets["Additional info"]["fields"])
        self.assertIn("is_staff", add_fieldsets["Additional info"]["fields"])
        self.assertIn(
            "years_of_experience",
            add_fieldsets["Additional info"]["fields"]
        )

    def test_article_list_display(self):
        url = reverse("admin:catalog_article_changelist")
        res = self.client.get(url)

        self.assertContains(res, self.article.title)
        self.assertContains(
            res,
            self.article.published_date.strftime("%Y-%m-%d")
        )

    def test_article_list_filter(self):
        model_admin = ArticleAdmin(Article, admin.site)
        self.assertEqual(model_admin.list_filter, ["title", "published_date"])

    def test_article_search_fields(self):
        model_admin = ArticleAdmin(Article, admin.site)
        self.assertEqual(model_admin.search_fields, ("title",))
