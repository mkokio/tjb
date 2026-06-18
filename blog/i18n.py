"""Lightweight UI-string localization for *the japan bike*.

The site supports exactly two languages, English (``en``) and Japanese (``ja``),
chosen by a single site-wide toggle in the top bar. The choice is persisted in a
cookie (``settings.LANGUAGE_COOKIE_NAME``) and applied by :class:`LanguageMiddleware`,
which activates Django's translation machinery so that ``get_language()`` returns
the active code everywhere (used by the model ``_en``/``_ja`` field pickers).

UI chrome strings live in the :data:`STRINGS` dict below rather than gettext
``.po`` files — this keeps the project dependency-free and skips the
message-compilation build step, while content translation lives on the models.
"""

from django.conf import settings
from django.utils import translation

from .models import Category, category_label

LANGS = ("en", "ja")
DEFAULT_LANG = "en"


# UI chrome strings. {x} placeholders are filled in templates via the `fmt` tag.
STRINGS = {
    "en": {
        "write": "Write",
        "search": "Search",
        "menu": "Menu",
        "your_profile": "Your profile",
        "language": "Language",
        # masthead
        "dateline_left": "Nippon · Two Wheels",
        "dateline_issue": "No. 07",
        # feed
        "story": "story",
        "stories": "stories",
        "show_all": "show all",
        # article
        "back": "back to all stories",
        "read": "read",
        "lang_en_name": "English",
        "lang_ja_name": "日本語",
        "originally_written": "Originally written in {x}",
        "viewing_translation": " · viewing translation",
        "coming_soon": "The full body of this story is coming soon.",
        "more_from": "more from {x}, see you on the next trail.",
        # profile
        "follow": "Follow",
        "handle": "handle",
        "stories_by": "Stories by {x}",
        "other_contributors": "Other contributors",
        # footer
        "footer_tag": "A reader-built zine for riding in Japan · 日本の自転車雑記",
        "footer_made": "© 2026 · Made in Shizuoka",
    },
    "ja": {
        "write": "書く",
        "search": "検索",
        "menu": "メニュー",
        "your_profile": "プロフィール",
        "language": "言語",
        "dateline_left": "日本 ・ 自転車",
        "dateline_issue": "第 七 号",
        "story": "件の記事",
        "stories": "件の記事",
        "show_all": "すべて表示",
        "back": "一覧へ戻る",
        "read": "で読めます",
        "lang_en_name": "English",
        "lang_ja_name": "日本語",
        "originally_written": "この記事は元々{x}で書かれました",
        "viewing_translation": "(翻訳版を表示中)",
        "coming_soon": "この記事の本文は近日公開予定です。",
        "more_from": "{x} より、また次のトレイルで。",
        "follow": "フォロー",
        "handle": "ハンドル",
        "stories_by": "{x} の記事",
        "other_contributors": "他の書き手",
        "footer_tag": "A reader-built zine for riding in Japan · 日本の自転車雑記",
        "footer_made": "© 2026 · Made in Shizuoka",
    },
}


def normalize(lang):
    return lang if lang in LANGS else DEFAULT_LANG


def get_lang(request):
    """Active language for this request, from the cookie (default English)."""
    return normalize(request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME, DEFAULT_LANG))


class LanguageMiddleware:
    """Activate the cookie-selected language for the duration of the request."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        lang = get_lang(request)
        translation.activate(lang)
        request.LANG = lang
        try:
            return self.get_response(request)
        finally:
            translation.deactivate()


def _masthead_date(lang):
    from django.utils import timezone
    now = timezone.localtime()
    if lang == "ja":
        return f"{now.year}年{now.month}月{now.day}日"
    return f"{now.strftime('%A, %B')} {now.day}, {now.year}"


def _css_version():
    """mtime of the stylesheet, used as a cache-buster query (?v=...) so edits
    to site.css are always picked up without a manual hard-refresh."""
    import os
    css = os.path.join(os.path.dirname(__file__), "static", "blog", "site.css")
    try:
        return int(os.path.getmtime(css))
    except OSError:
        return 0


def language_context(request):
    """Inject UI language helpers into every template."""
    lang = getattr(request, "LANG", None) or get_lang(request)
    return {
        "LANG": lang,
        "LANG_OTHER": "ja" if lang == "en" else "en",
        "T": STRINGS[lang],
        "MASTHEAD_DATE": _masthead_date(lang),
        "CSS_VERSION": _css_version(),
        "NAV_CATEGORIES": [
            {"slug": c.value, "label": category_label(c.value, lang)}
            for c in Category
        ],
    }
