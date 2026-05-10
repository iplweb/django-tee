from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tee", "0002_auto_20211031_2122"),
    ]

    operations = [
        migrations.AddField(
            model_name="log",
            name="traceback",
            field=models.TextField(blank=True, null=True),
        ),
    ]
