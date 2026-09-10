from django.db import migrations


def fix_bad_records(apps, schema_editor):
    CompetitionPhoto = apps.get_model("core", "CompetitionPhoto")
    for p in CompetitionPhoto.objects.filter(color="competencia"):
        parts = p.filename.split("/", 1)
        if len(parts) == 2:
            p.color = parts[0]
            p.filename = parts[1]
            p.save(update_fields=["color", "filename"])


def reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0015_biblebook_challenge_chapter_end_and_more"),
    ]

    operations = [
        migrations.RunPython(fix_bad_records, reverse),
    ]
