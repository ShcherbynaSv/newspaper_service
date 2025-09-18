from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from catalog.models import Topic, Article


class ModelsTests(TestCase):
    def setUp(self):
        self.topic = Topic.objects.create(name="test-topic")
        self.username = "test-username"
        self.password = "test-password"
        self.redactor = get_user_model().objects.create_user(
            username=self.username,
            password=self.password
        )
        self.article=Article.objects.create(
            title="test-title",
            content="test-content",
            published_date="2025-09-25"
        )
        self.article.redactors.set([self.redactor])
        self.article.topics.set([self.topic])

    def test_topic_str(self):
        self.assertEqual(str(self.topic), self.topic.name)

    def test_redactor_with_years_of_experience(self):
        self.redactor.years_of_experience = 10
        self.assertEqual(self.redactor.username, self.username)
        self.assertTrue(self.redactor.check_password(self.password))
        self.assertEqual(self.redactor.years_of_experience, 10)

    def test_redactor_get_absolute_url(self):
        expected_url = reverse("catalog:redactor-detail", args=[str(self.redactor.pk)])
        self.assertEqual(self.redactor.get_absolute_url(), expected_url)

    def test_article_str(self):
        self.assertEqual(str(self.article), self.article.title)

    def test_article_get_absolute_url(self):
        expected_url = reverse("catalog:article-detail", args=[str(self.article.pk)])
        self.assertEqual(self.article.get_absolute_url(), expected_url)
