# Historical initial migration. Cleaned of pre-Django-4.0 imports
# (django.contrib.postgres.fields.jsonb) but the migration name is
# preserved so that installations that previously had a "tee" app
# applied (with the same migration history) remain compatible.

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Log",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("started_on", models.DateTimeField(auto_now_add=True)),
                ("finished_on", models.DateTimeField(blank=True, null=True)),
                ("exitcode", models.SmallIntegerField(blank=True, null=True)),
                ("command_name", models.TextField()),
                ("args", models.JSONField(blank=True, null=True)),
                ("kwargs", models.JSONField(blank=True, null=True)),
                ("stdout", models.TextField(blank=True, null=True)),
                ("stderr", models.TextField(blank=True, null=True)),
            ],
        ),
    ]
