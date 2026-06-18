from django.contrib import admin

from .models import Author, Post


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("name", "handle", "writes")
    prepopulated_fields = {"slug": ("name",)}
    fieldsets = (
        (None, {"fields": ("name", "slug", "handle", "avatar", "writes")}),
        ("English", {"fields": ("role_en", "location_en", "since_en", "bio_en")}),
        ("日本語", {"fields": ("role_ja", "location_ja", "since_ja", "bio_ja")}),
    )


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("__str__", "category", "author", "date", "orig", "published")
    list_filter = ("category", "published", "orig", "author")
    date_hierarchy = "date"
    prepopulated_fields = {"slug": ("title_en",)}
    fieldsets = (
        (None, {"fields": ("slug", "category", "author", "date", "read_time", "orig", "published")}),
        ("Media", {"fields": ("image", "media_label", "media_shape")}),
        ("English", {"fields": ("title_en", "sub_en", "body_en")}),
        ("日本語", {"fields": ("title_ja", "sub_ja", "body_ja")}),
    )
