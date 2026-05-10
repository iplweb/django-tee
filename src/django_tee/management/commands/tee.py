import sys

from django.core.management import BaseCommand

from django_tee import core


class Command(BaseCommand):
    help = (
        "Run another Django management command, capturing stdout/stderr/"
        "traceback into a django_tee.Log row. Output also still lands on "
        "the terminal, so this is safe to use as a transparent wrapper "
        "for cron jobs."
    )

    def add_arguments(self, parser):
        parser.add_argument("command_name", help="Django command to execute")
        parser.add_argument(
            "otherthings",
            nargs="*",
            help="Arguments forwarded to the wrapped command",
        )

    def handle(self, command_name, otherthings, *args, **options):
        new_argv = [sys.argv[0], command_name] + otherthings

        kwargs = {}

        for elem in ["stdout", "stderr"]:
            if options.get(elem):
                kwargs[elem] = options.get(elem)

        core.execute(new_argv, **kwargs)
