"""Small template helpers for *the japan bike*."""

from django import template

register = template.Library()


@register.filter
def fmt(value, arg):
    """Fill a single ``{x}`` placeholder in a UI string.

    Usage: ``{{ T.stories_by|fmt:author.name }}``
    """
    if value is None:
        return ""
    return str(value).replace("{x}", str(arg))


@register.simple_tag
def avatar_style(text, size=42):
    """Inline style for an avatar circle whose handwritten initials (1–3 chars)
    scale down to keep fitting as they get longer — mirrors the prototype."""
    n = len([c for c in str(text)][:3])
    factor = 0.30 if n >= 3 else 0.40 if n == 2 else 0.52
    pad = "0 2px" if n >= 2 else "0"
    return (
        f"width:{size}px;height:{size}px;"
        f"font-size:{round(size * factor)}px;line-height:1;padding:{pad}"
    )
