from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tee", "0005_django32"),
    ]

    operations = [
        migrations.AlterField(
            model_name="log",
            name="finished_successfully",
            field=models.BooleanField(blank=True, default=None, null=True),
        ),
    ]
