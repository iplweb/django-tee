from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("tee", "0006_nullbooleanfield"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="log",
            options={
                "ordering": ["-started_on"],
                "verbose_name": "command log",
                "verbose_name_plural": "command logs",
            },
        ),
    ]
