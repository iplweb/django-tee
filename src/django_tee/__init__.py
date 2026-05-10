"""django-tee — capture Django management command stdout/stderr/traceback to DB.

Public API:
    from django_tee.core import execute   # programmatic invocation
    from django_tee.models import Log     # log records
"""

default_app_config = "django_tee.apps.DjangoTeeConfig"
