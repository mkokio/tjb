"""Remap retired category values to the new fixed set.

Bikes & Parts merged into "Bike/Parts" (slug ``bikes``); the retired "Culture"
category folds into "Other". Reversible: the old slugs can't be reconstructed,
so the reverse is a no-op (the merged rows simply keep their new values).
"""

from django.db import migrations

REMAP = {
    "parts": "bikes",
    "culture": "other",
}


def remap_forward(apps, schema_editor):
    Post = apps.get_model("blog", "Post")
    for old, new in REMAP.items():
        Post.objects.filter(category=old).update(category=new)


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0002_alter_post_category"),
    ]

    operations = [
        migrations.RunPython(remap_forward, migrations.RunPython.noop),
    ]
