from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from catalog.models import Redactor, Topic, Article


@admin.register(Redactor)
class RedactorAdmin(UserAdmin):
    list_display = UserAdmin.list_display  + ("years_of_experience",)
    list_filter = UserAdmin.list_filter + ("years_of_experience",)
    fieldsets = UserAdmin.fieldsets + (("Additional info", {"fields": ("years_of_experience",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("Additional info", {"fields": ("first_name", "last_name", "is_staff", "years_of_experience",)}),)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ["title", "published_date"]
    list_filter = ["title", "published_date"]
    search_fields = ("title",)


admin.site.register(Topic)

