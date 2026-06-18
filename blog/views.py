"""Server-rendered views. No client router, no API, no JSON endpoints."""

from django.conf import settings
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .i18n import normalize
from .models import Author, Category, Post, category_label


def _published():
    return Post.objects.filter(published=True).select_related("author")


def feed(request, cat_slug=None):
    active_cat = None
    posts = _published()
    if cat_slug is not None:
        if cat_slug not in Category.values:  # validate against the fixed enum
            raise Http404("Unknown category")
        active_cat = cat_slug
        posts = posts.filter(category=active_cat)
    return render(request, "blog/feed.html", {
        "posts": posts,
        "active_cat": active_cat,
        "active_cat_label": category_label(active_cat, request.LANG) if active_cat else None,
    })


def article(request, slug):
    post = get_object_or_404(_published(), slug=slug)
    orig_name = "English" if post.orig == "en" else "日本語"
    return render(request, "blog/article.html", {
        "post": post,
        "orig_name": orig_name,
    })


def profile(request, slug):
    author = get_object_or_404(Author, slug=slug)
    posts = _published().filter(author=author)
    return render(request, "blog/profile.html", {
        "author": author,
        "posts": posts,
        "story_count": posts.count(),
        "others": Author.objects.exclude(pk=author.pk),
    })


@require_POST
def set_language(request):
    """Persist the chosen UI language in a cookie and redirect back.

    POST-only (Django i18n convention): the form submits ``language`` (en|ja)
    and a ``next`` URL. The whole page re-renders server-side — no JavaScript,
    no SPA behaviour. Safe-redirects to ``next`` on the same host only.
    """
    lang = normalize(request.POST.get("language", "en"))
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or reverse("blog:feed")
    if not url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        next_url = reverse("blog:feed")
    response = HttpResponseRedirect(next_url)
    response.set_cookie(
        settings.LANGUAGE_COOKIE_NAME, lang,
        max_age=settings.LANGUAGE_COOKIE_AGE, samesite="Lax",
    )
    return response
