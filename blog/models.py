"""Data model for *the japan bike*.

Two kinds of "language" live here (see the handoff README):

* **UI chrome** (nav labels, buttons) -> handled in ``blog.i18n``, not the DB.
* **Content** (titles, bodies, bios) -> stored in *paired* ``_en`` / ``_ja``
  fields on these models. Whichever language the reader has selected is picked
  at render time via :func:`django.utils.translation.get_language`; if that
  version is blank we fall back to the language the piece was *written* in
  (``orig`` / ``writes``) and flag it as a translation.
"""

from django.db import models
from django.utils.translation import get_language


# Categories are a FIXED enum (max 7), not free-form tags -> stable nav,
# clean /c/<slug>/ URLs, no orphans. English labels live on the choices;
# the Japanese display label is a presentation concern, mapped below.
class Category(models.TextChoices):
    BIKES = "bikes", "Bike/Parts"
    PLACES = "places", "Places"
    OPINIONS = "opinions", "Opinions"
    INTERVIEWS = "interviews", "Interviews"
    OTHER = "other", "Other"


CATEGORY_JP = {
    "bikes": "バイク/パーツ",
    "places": "走る場所",
    "opinions": "オピニオン",
    "interviews": "インタビュー",
    "other": "その他",
}


def category_label(value, lang=None):
    """Localized display label for a category value."""
    lang = lang or get_language()
    if lang == "ja":
        return CATEGORY_JP.get(value, value)
    return Category(value).label


class LangChoices(models.TextChoices):
    EN = "en", "English"
    JA = "ja", "日本語"


def _format_date(d, lang):
    if d is None:
        return ""
    if lang == "ja":
        return f"{d.year}年{d.month}月{d.day}日"
    return f"{d.strftime('%B')} {d.day}, {d.year}"


class Author(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=80, unique=True)
    handle = models.CharField(max_length=40, help_text="e.g. @marc")
    # 1–3 character handle drawn in the circular avatar (e.g. マーク / M).
    avatar = models.CharField(max_length=8, blank=True)
    writes = models.CharField(max_length=2, choices=LangChoices.choices, default=LangChoices.EN)

    location_en = models.CharField(max_length=80, blank=True)
    location_ja = models.CharField(max_length=80, blank=True)
    role_en = models.CharField(max_length=120, blank=True)
    role_ja = models.CharField(max_length=120, blank=True)
    since_en = models.CharField(max_length=120, blank=True)
    since_ja = models.CharField(max_length=120, blank=True)
    bio_en = models.TextField(blank=True)
    bio_ja = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("blog:profile", args=[self.slug])

    def _loc(self, base):
        lang = get_language()
        return getattr(self, f"{base}_ja") if lang == "ja" else getattr(self, f"{base}_en")

    @property
    def location(self):
        return self._loc("location")

    @property
    def role(self):
        return self._loc("role")

    @property
    def since(self):
        return self._loc("since")

    @property
    def bio(self):
        return self._loc("bio")

    @property
    def avatar_text(self):
        return self.avatar or (self.name[:1] if self.name else "")

    @property
    def writes_label(self):
        # Fixed to the author's own writing language, independent of UI lang.
        return "Writes in English" if self.writes == "en" else "日本語で執筆"


class Post(models.Model):
    slug = models.SlugField(max_length=120, unique=True)
    category = models.CharField(max_length=20, choices=Category.choices)
    author = models.ForeignKey(Author, on_delete=models.PROTECT, related_name="posts")
    date = models.DateField()
    orig = models.CharField(
        max_length=2, choices=LangChoices.choices, default=LangChoices.EN,
        help_text="The language this story was originally written in.",
    )

    title_en = models.CharField(max_length=200, blank=True)
    title_ja = models.CharField(max_length=200, blank=True)
    sub_en = models.CharField(max_length=400, blank=True)
    sub_ja = models.CharField(max_length=400, blank=True)

    # Ordered list of typed content blocks. Each block is a dict, one of:
    #   {"t": "p", "x": "<paragraph text>"}
    #   {"t": "quote", "x": "<pull-quote text>"}
    #   {"t": "img", "label": "<placeholder label>", "cap": "<caption>"}
    #   {"t": "ol", "items": ["...", "..."]}
    #   {"t": "code", "x": "<code text>"}
    body_en = models.JSONField(default=list, blank=True)
    body_ja = models.JSONField(default=list, blank=True)

    # Real photography (optional). Falls back to a striped placeholder labelled
    # `media_label` with the given aspect `media_shape` when absent.
    image = models.ImageField(upload_to="posts/", blank=True, null=True)
    media_label = models.CharField(max_length=80, blank=True)
    media_shape = models.CharField(
        max_length=8, default="wide",
        choices=[("wide", "16:9"), ("", "4:3"), ("tall", "3:4")],
    )

    published = models.BooleanField(default=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return self.title_en or self.title_ja or self.slug

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("blog:article", args=[self.slug])

    @property
    def category_label(self):
        return category_label(self.category)

    @property
    def orig_chip(self):
        # The post's ORIGINAL language, shown as a small chip in the feed.
        return "EN" if self.orig == "en" else "日本語"

    @property
    def display_date(self):
        return _format_date(self.date, get_language())

    # ---- content, with fall-back to the original language --------------------
    @property
    def _view(self):
        return get_language()

    @property
    def is_translation(self):
        return self._view != self.orig

    @property
    def title(self):
        v = self._view
        return getattr(self, f"title_{v}") or getattr(self, f"title_{self.orig}")

    @property
    def sub(self):
        v = self._view
        return getattr(self, f"sub_{v}") or getattr(self, f"sub_{self.orig}")

    @property
    def body(self):
        v = self._view
        return getattr(self, f"body_{v}") or getattr(self, f"body_{self.orig}")

    @property
    def has_body(self):
        return bool(self.body)

    # ---- machine translation (admin-only; see blog/translation.py) -----------
    def _other_lang(self):
        return "ja" if self.orig == "en" else "en"

    def translation_is_empty(self):
        """True if the non-original language has no content yet."""
        t = self._other_lang()
        return not (getattr(self, f"title_{t}") or getattr(self, f"sub_{t}")
                    or getattr(self, f"body_{t}"))

    def machine_translate(self):
        """Fill the non-original language fields from the original via MT.

        Overwrites the target side — callers decide *when* this runs (on create,
        or via the explicit admin button/action), so a human translation is only
        ever replaced when you ask for it.
        """
        from .translation import make_translator, translate_text, translate_blocks
        src, tgt = self.orig, self._other_lang()
        tr = make_translator(src, tgt)
        title_max = self._meta.get_field(f"title_{tgt}").max_length
        sub_max = self._meta.get_field(f"sub_{tgt}").max_length
        setattr(self, f"title_{tgt}", translate_text(tr, getattr(self, f"title_{src}"))[:title_max])
        setattr(self, f"sub_{tgt}", translate_text(tr, getattr(self, f"sub_{src}"))[:sub_max])
        setattr(self, f"body_{tgt}", translate_blocks(tr, getattr(self, f"body_{src}")))
