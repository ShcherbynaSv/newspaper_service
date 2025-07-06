from django.contrib.auth.models import AbstractUser
from django.db import models

from newspaper_service import settings


class Topic(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class Redactor(AbstractUser):
    years_of_experience = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ("username",)


class Article(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    published_date = models.DateField()
    topics = models.ManyToManyField(Topic, related_name="articles")
    redactors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="articles"
    )

    def __str__(self):
        return self.title
