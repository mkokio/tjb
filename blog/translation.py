"""Machine translation for post content (deep-translator → Google, free, no key).

Runs server-side in the admin ONLY. Results are written to the DB, so the public
site never calls a translation service — it stays zero-JS with no extra network
requests for readers. Our language codes ("en"/"ja") already match Google's.
"""

from deep_translator import GoogleTranslator


def make_translator(source, target):
    return GoogleTranslator(source=source, target=target)


def _t(translator, text):
    text = (text or "").strip()
    if not text:
        return ""
    return translator.translate(text)


def translate_text(translator, text):
    return _t(translator, text)


def translate_blocks(translator, blocks):
    """Translate the text inside body blocks, preserving structure. Code blocks
    are deliberately left untranslated."""
    out = []
    for b in (blocks or []):
        nb = dict(b)
        kind = nb.get("t")
        if kind in ("p", "quote"):
            nb["x"] = _t(translator, nb.get("x", ""))
        elif kind == "img":
            nb["label"] = _t(translator, nb.get("label", ""))
            nb["cap"] = _t(translator, nb.get("cap", ""))
        elif kind == "ol":
            nb["items"] = [_t(translator, it) for it in nb.get("items", [])]
        out.append(nb)
    return out
