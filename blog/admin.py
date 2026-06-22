from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django import forms
from .widgets import BlockEditorWidget
from .models import Author, Post

class PostAdminForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = '__all__'
        widgets = {
            'body_en': BlockEditorWidget(),
            'body_ja': BlockEditorWidget(),
        }
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
    form = PostAdminForm
    list_display = ("__str__", "category", "author", "date", "orig", "published")
    list_filter = ("category", "published", "orig", "author")
    date_hierarchy = "date"
    prepopulated_fields = {"slug": ("title_en",)}
    change_form_template = "admin/blog/post/change_form.html"
    actions = ["autotranslate_action"]
    fieldsets = (
        (None, {
            "fields": ("slug", "category", "author", "date", "orig", "published"),
            "description": (
                "Write in the post's original language below. On <b>create</b>, if the "
                "other language is left blank it's machine-translated automatically. "
                "Editing later never auto-translates — use “Save and auto-translate the "
                "other language” to refresh the machine translation on demand."
            ),
        }),
        ("Media", {"fields": ("image", "media_label", "media_shape")}),
        ("English", {"fields": ("title_en", "sub_en", "body_en")}),
        ("日本語", {"fields": ("title_ja", "sub_ja", "body_ja")}),
    )

    # ---- machine-translation orchestration -----------------------------------
    def _do_translate(self, request, obj):
        try:
            obj.machine_translate()
            obj.save()
            self.message_user(
                request,
                f"Auto-translated “{obj}” into {obj._other_lang().upper()} from the original.",
                level=messages.SUCCESS,
            )
        except Exception as exc:  # never let a translation hiccup lose the user's work
            self.message_user(
                request,
                f"Auto-translation failed for “{obj}” ({exc}). The post was saved; "
                f"try the auto-translate button again.",
                level=messages.WARNING,
            )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # On CREATE only, and only if the other language wasn't filled in by hand.
        if not change and obj.translation_is_empty():
            self._do_translate(request, obj)

    def response_change(self, request, obj):
        if "_autotranslate" in request.POST:
            self._do_translate(request, obj)
            return HttpResponseRedirect(request.get_full_path())
        return super().response_change(request, obj)

    def response_add(self, request, obj, post_url_continue=None):
        if "_autotranslate" in request.POST and not obj.translation_is_empty():
            # create-time save_model already translated an empty side; only needed
            # here if the user pre-filled then asked to overwrite.
            self._do_translate(request, obj)
        return super().response_add(request, obj, post_url_continue)

    @admin.action(description="Auto-translate the other language from the original (overwrites)")
    def autotranslate_action(self, request, queryset):
        for obj in queryset:
            self._do_translate(request, obj)
