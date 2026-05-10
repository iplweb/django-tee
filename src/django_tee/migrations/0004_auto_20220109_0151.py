# Cleaned of NullBooleanField (removed in Django 5.0). The field is
# created here in its final BooleanField(null=True) shape — migrations
# 0005 and 0006 (which historically promoted NullBooleanField to a
# nullable BooleanField) become effective no-ops on a fresh DB but are
# kept so installations carrying the original migration history stay
# in sync.

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tee", "0003_log_traceback"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="log",
            name="exit_code",
        ),
        migrations.RemoveField(
            model_name="log",
            name="exit_value",
        ),
        migrations.RemoveField(
            model_name="log",
            name="kwargs",
        ),
        migrations.AddField(
            model_name="log",
            name="finished_successfully",
            field=models.BooleanField(blank=True, default=None, null=True),
        ),
    ]
