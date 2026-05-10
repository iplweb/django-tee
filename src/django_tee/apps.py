from django.apps import AppConfig


class DjangoTeeConfig(AppConfig):
    name = "django_tee"
    # Keep label = "tee" so existing installations that previously had a
    # `tee` app (e.g. inlined in another Django project) can drop in
    # django-tee without renaming tables, content types, or rewriting
    # `django_migrations` rows.
    label = "tee"
    verbose_name = "Tee — captured command output"
    default_auto_field = "django.db.models.AutoField"
