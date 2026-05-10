from django.contrib import admin
from django.utils.safestring import mark_safe

from django_tee.models import Log
from django_tee.utils import last_n_lines


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = [
        "cmd_name",
        "started_on",
        "finished_on",
        "finished_successfully",
        "last_5_lines",
    ]

    list_per_page = 10

    readonly_fields = [
        "started_on",
        "finished_on",
        "finished_successfully",
        "command_name",
        "args",
        "stdout",
        "stderr",
        "traceback",
    ]

    date_hierarchy = "started_on"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(description="Command")
    def cmd_name(self, obj):
        args = ""
        if obj.args:
            args = f" {' '.join(obj.args)}"
        return f"{obj.command_name}" + args

    @admin.display(description="Results")
    def last_5_lines(self, obj):
        s = obj.stderr

        if obj.traceback:
            s = obj.traceback

        if not s:
            s = obj.stdout

        r = last_n_lines(s, nlines=5)
        if r is None:
            return None
        return mark_safe(f"<pre>{r}</pre>")
