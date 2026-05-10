from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tee", "0004_auto_20220109_0151"),
    ]

    operations = [
        migrations.AlterField(
            model_name="log",
            name="args",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="log",
            name="finished_successfully",
            field=models.BooleanField(null=True),
        ),
    ]
