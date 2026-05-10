from django.db import models


class Log(models.Model):
    started_on = models.DateTimeField(auto_now_add=True)
    finished_on = models.DateTimeField(blank=True, null=True)
    finished_successfully = models.BooleanField(null=True, blank=True, default=None)

    command_name = models.TextField()
    args = models.JSONField(blank=True, null=True)

    stdout = models.TextField(blank=True, null=True)
    stderr = models.TextField(blank=True, null=True)
    traceback = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "command log"
        verbose_name_plural = "command logs"
        ordering = ["-started_on"]

    def __str__(self):
        return f'Results of command "{self.command_name}" ran on {self.started_on}'
