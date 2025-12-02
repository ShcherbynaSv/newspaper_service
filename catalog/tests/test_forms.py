from django.test import TestCase
from django.contrib.auth import get_user_model

from catalog.forms import (
    RedactorCreationForm,
    RedactorUpdateForm,
    ArticleForm,
    TopicSearchForm,
    ArticleSearchForm,
    RedactorSearchForm,
)
from catalog.models import Redactor, Topic


class RedactorCreationFormTests(TestCase):
    def test_valid_data(self):
        form = RedactorCreationForm(
            data={
                "username": "test_user",
                "password1": "StrongPass123",
                "password2": "StrongPass123",
                "first_name": "John",
                "last_name": "Doe",
                "years_of_experience": 5,
            }
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_missing_required_fields(self):
        form = RedactorCreationForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)
        self.assertIn("password1", form.errors)


class RedactorUpdateFormTests(TestCase):
    def setUp(self):
        self.redactor = get_user_model().objects.create_user(
            username="old_user", password="test12345", years_of_experience=3
        )

    def test_update_valid(self):
        form = RedactorUpdateForm(
            data={
                "username": "new_user",
                "first_name": "Test",
                "last_name": "User",
                "email": "test@example.com",
                "years_of_experience": 10,
            },
            instance=self.redactor,
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_missing_username(self):
        form = RedactorUpdateForm(data={}, instance=self.redactor)
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)


class ArticleFormTests(TestCase):
    def setUp(self):
        self.redactor1 = get_user_model().objects.create_user(
            username="redactor-1", password="pass-1"
        )
        self.redactor2 = get_user_model().objects.create_user(
            username="redactor-2", password="pass-2"
        )

        self.topic1 = Topic.objects.create(name="Culture")
        self.topic2 = Topic.objects.create(name="Politics")

    def test_valid_article(self):
        form = ArticleForm(
            data={
                "title": "Test-article",
                "content": "Test-article-content",
                "published_date": "2025-10-15",
                "topics": [self.topic1.id, self.topic2.id],
                "redactors": [self.redactor1.id, self.redactor2.id],
            }
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_missing_required(self):
        form = ArticleForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)
        self.assertIn("content", form.errors)
        self.assertIn("published_date", form.errors)
        self.assertIn("topics", form.errors)
        self.assertIn("redactors", form.errors)


class SearchFormTests(TestCase):
    def test_topic_search_form(self):
        form = TopicSearchForm(data={"name": "Cul"})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["name"], "Cul")

    def test_article_search_form(self):
        form = ArticleSearchForm(data={"title": "New"})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["title"], "New")

    def test_redactor_search_form(self):
        form = RedactorSearchForm(data={"full_name": "John Doe"})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["full_name"], "John Doe")
