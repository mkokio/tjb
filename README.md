# the japan bike

A bilingual (English / 日本語) editorial site for mountain-biking in Japan,
recreated from the design handoff as a server-rendered Django project.

**Design goals met:**
- **Zero JavaScript** on the public site — verified, no `<script>` tags. The
  mobile menu is a pure-CSS checkbox toggle; the EN/日本語 switch is a small POST
  form (no JS).
- **Minimal network footprint** — one stylesheet, one Google Fonts request, the
  nameplate image, and page assets. No client router, no API/XHR, no analytics,
  no bundles.
- **SQLite** by default; swap `DATABASES` in `thejapanbike/settings.py` for
  Postgres/MySQL later with no code changes.
- Runs on **Django 6.0** (see `requirements.txt`).

## Run it

```bash
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
./venv/bin/python manage.py migrate
./venv/bin/python manage.py seed_demo        # sample bilingual content
./venv/bin/python manage.py createsuperuser  # if you didn't already
./venv/bin/python manage.py runserver
```

Then open http://127.0.0.1:8000/. A demo admin (`admin` / `admin`) was created
during setup — change the password before deploying anywhere.

## How it works

### Two kinds of "language"
- **UI chrome** (nav, buttons, "back to all stories") — a lightweight strings
  dict in [`blog/i18n.py`](blog/i18n.py), no gettext/`.po` compile step.
- **Content** (titles, bodies, bios) — stored as paired `_en` / `_ja` fields on
  the models. The active language is picked at render time; if a translation is
  missing it falls back to the language the piece was *written* in (`orig`) and
  flags itself as a translation.

### The language switch
A single site-wide toggle anchored to the right end of the top bar — two
monocolor icon buttons (a maple leaf = English, a rising-sun flag = 日本語),
themed to the site's `--ink` / `--ink-soft` tokens via `currentColor`, with the
active option raised and the inactive dimmed. It's a small POST form (with CSRF)
to `blog:set_language`, which stores the choice in the `tjb_lang` cookie and
redirects back — no JavaScript, full server-side re-render. `LanguageMiddleware`
activates the choice so `get_language()` drives both the UI strings and the
content field pickers.

It's placed last in the action group so it pins to the bar's right edge and
never shifts when other controls (e.g. the Write button) change width between
languages.

> Fun quirk, as designed: the nav wordmark shows the *opposite* language to the
> one selected (English active → 「ザ ジャパンバイク。」; 日本語 active → "the
> japan bike.").

### Authoring
Content is authored in the **Django admin** (`/admin/`). Posts carry both
language versions plus a JSON body of typed blocks (`p`, `quote`, `img`, `ol`,
`code`) that render with the neumorphic pull-quote / circled-counter / code
styling. Real photography uploads via the `image` field; absent that, a striped
placeholder labelled `media_label` is shown.

### Machine translation
Write a post in its original language and leave the other language blank — on
**create**, the empty side is machine-translated and stored (title, subtitle,
and body blocks; `code` blocks are left untouched). Filling both languages by
hand on creation skips translation and keeps what you wrote.

**Editing never auto-translates**, so a human translator's work is never
clobbered. To deliberately refresh the machine translation after revising the
original, use either the **"Save and auto-translate the other language"** button
in the post editor, or the **"Auto-translate the other language…"** bulk action
on the post list (both overwrite the other side from the original).

All of this runs **server-side in the admin** ([`blog/translation.py`](blog/translation.py))
and is written to the DB, so the public site makes **no** translation calls and
stays zero-JS — readers only ever get the stored text. Failures are caught: the
post still saves and you get a warning to retry.

The default backend is `deep-translator` → Google (free, no API key, but an
unofficial endpoint that can rate-limit). **Swapping providers is one line** in
`make_translator()` — e.g. for DeepL's free tier (best EN↔JA quality, needs a
free key):

```python
# blog/translation.py
from deep_translator import DeeplTranslator   # instead of GoogleTranslator

def make_translator(source, target):
    return DeeplTranslator(api_key="…", source=source, target=target)
    # other drop-in options: MyMemoryTranslator (no key) · LibreTranslator (self-host)
```

## Project layout
```
thejapanbike/settings.py   # sqlite, cookie language, static/media
blog/
  models.py                # Author, Post, Category (fixed enum), body blocks
  views.py                 # feed, article, profile, category, set_language
  i18n.py                  # UI strings + language middleware + context processor
  translation.py           # admin-only machine translation (deep-translator)
  admin.py                 # bilingual authoring + auto-translate button/action
  templatetags/tjb.py      # {x} string interpolation, avatar sizing
  templates/blog/          # base + partials + feed/article/profile pages
  static/blog/site.css     # the design system (lifted from the prototype)
  static/blog/tiretrack.png        # fixed background graphic
  static/blog/thejapanbike_title.png  # masthead nameplate image
  management/commands/seed_demo.py
```

## Notes
- **Masthead nameplate** is an image (`static/blog/thejapanbike_title.png`),
  capped at `max-width: 100%` and sized with `clamp()` so it scales with the
  viewport. Swap the file to change the nameplate.
- **Fonts** are loaded from Google Fonts in a single request — Caveat, DM Serif
  Display, Shippori Mincho B1, Noto Serif JP, and the gothic display face
  **Grenze Gotisch** (a legible blackletter; the prototype's `UnifrakturMaguntia`
  was dropped). The JP serif faces are large, so Google's optimized, cached CDN
  is lighter for users than self-hosting full Japanese fonts. To go fully
  self-hosted, download the woff2s into `static/blog/` and add `@font-face` rules.
- The neumorphic palette/geometry live in `:root` at the top of `site.css`
  (shipped "Newsprint" palette, rust accent). Tweak in one place.
- `site.css` is loaded with a `?v=<mtime>` cache-buster (computed in
  `blog/i18n.py`) so edits always load fresh without a manual hard-refresh.
- The seven prototype categories were reduced to five — **Bike/Parts, Places,
  Opinions, Interviews, Other** — a fixed `TextChoices` enum on `Post.category`.
