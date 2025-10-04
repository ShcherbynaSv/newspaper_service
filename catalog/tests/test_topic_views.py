from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from catalog.models import Topic


class TopicViewTests(TestCase):
    def setUp(self):
        self.url = reverse("catalog:topic-list")

    def test_template_and_context(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/topic_list.html")
        self.assertIn("topic_list", response.context)
        self.assertIn("search_form", response.context)

    def test_queryset_no_filter_returns_all(self):
        Topic.objects.create(name="Culture")
        Topic.objects.create(name="Politics")

        response = self.client.get(self.url)
        topics = Topic.objects.all()
        self.assertEqual(
            list(response.context["topic_list"]),
            list(topics)
        )

    def test_queryset_with_filter_returns_matching(self):
        Topic.objects.create(name="Culture")
        Topic.objects.create(name="Politics")

        response = self.client.get(self.url, {"name": "cul"})
        topics = Topic.objects.filter(name__icontains="cul")
        self.assertEqual(
            list(response.context["topic_list"]),
            list(topics)
        )

    def test_queryset_with_filter_no_match(self):
        Topic.objects.create(name="Culture")

        response = self.client.get(self.url, {"name": "politics"})
        self.assertEqual(list(response.context["topic_list"]), [])

    def test_pagination_first_page(self):
        Topic.objects.bulk_create(
            [Topic(name=f"Topic {i}") for i in range(15)]
        )

        response = self.client.get(self.url)
        page_obj = response.context["page_obj"]

        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(page_obj.paginator.num_pages, 2)
        self.assertEqual(len(response.context["topic_list"]), 10)

    def test_pagination_second_page(self):
        Topic.objects.bulk_create(
            [Topic(name=f"Topic {i}") for i in range(15)]
        )

        response = self.client.get(self.url, {"page": 2})
        page_obj = response.context["page_obj"]

        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(page_obj.paginator.num_pages, 2)
        self.assertEqual(len(response.context["topic_list"]), 5)

    def test_empty_database(self):
        response = self.client.get(self.url)
        self.assertEqual(list(response.context["topic_list"]), [])


class PublicTopicCreateViewTests(TestCase):
    def setUp(self):
        self.url = reverse("catalog:topic-create")
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="password1234"
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        login_url = reverse("login")
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"{login_url}?next={self.url}")


class PrivateTopicCreateViewTests(TestCase):
    def setUp(self):
        self.url = reverse("catalog:topic-create")
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="password1234"
        )
        self.client.force_login(self.user)

    def test_logged_in_user_can_access_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/topic_form.html")
        self.assertIn("form", response.context)

    def test_create_topic_valid_post(self):
        data = {"name": "Culture"}
        response = self.client.post(self.url, data)
        self.assertEqual(Topic.objects.count(), 1)
        self.assertEqual(Topic.objects.first().name, "Culture")
        self.assertRedirects(response, reverse("catalog:topic-list"))

    def test_create_topic_invalid_post(self):
        response = self.client.post(self.url, {"name": ""})
        form = response.context["form"]
        self.assertTrue(form.errors)
        self.assertIn("name", form.errors)
        self.assertEqual(form.errors["name"], ["This field is required."])
        self.assertEqual(Topic.objects.count(), 0)


class PublicTopicUpdateViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="password123"
        )
        self.topic = Topic.objects.create(name="Culture")
        self.url = reverse(
            "catalog:topic-update",
            args=[self.topic.id]
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")


class PrivateTopicUpdateViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="password123"
        )
        self.client.force_login(self.user)
        self.topic = Topic.objects.create(name="Culture")
        self.url = reverse(
            "catalog:topic-update",
            args=[self.topic.id]
        )

    def test_logged_in_user_can_access_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/topic_form.html")
        self.assertIn("form", response.context)
        self.assertEqual(response.context["form"].initial["name"], "Culture")

    def test_update_topic_valid_post(self):
        response = self.client.post(self.url, {"name": "Politics"})
        self.topic.refresh_from_db()
        self.assertEqual(self.topic.name, "Politics")
        self.assertRedirects(response, reverse("catalog:topic-list"))

    def test_update_topic_invalid_post(self):
        response = self.client.post(self.url, {"name": ""})
        form = response.context["form"]
        self.assertTrue(form.errors)
        self.topic.refresh_from_db()
        self.assertEqual(self.topic.name, "Culture")

    def test_update_nonexistent_object_returns_404(self):
        bad_url = reverse("catalog:topic-update", args=[999])
        response = self.client.get(bad_url)
        self.assertEqual(response.status_code, 404)


class PublicTopicDeleteViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="password1234"
        )
        self.topic = Topic.objects.create(name="Culture")
        self.url = reverse(
            "catalog:topic-delete",
            args=[self.topic.id]
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")


class PrivateTopicDeleteViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="password1234"
        )
        self.client.force_login(self.user)
        self.topic = Topic.objects.create(name="Culture")
        self.url = reverse(
            "catalog:topic-delete",
            args=[self.topic.id]
        )

    def test_logged_in_user_can_access_confirmation_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "catalog/confirm_delete_topic.html"
        )
        self.assertEqual(response.context["object"], self.topic)

    def test_delete_topic_valid_post(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse("catalog:topic-list"))
        self.assertFalse(
            Topic.objects.filter(id=self.topic.id).exists()
        )

    def test_get_request_does_not_delete_object(self):
        self.client.get(self.url)
        self.assertTrue(Topic.objects.filter(id=self.topic.id).exists())

    def test_delete_nonexistent_object_returns_404(self):
        bad_url = reverse("catalog:topic-delete", args=[999])
        response = self.client.get(bad_url)
        self.assertEqual(response.status_code, 404)
