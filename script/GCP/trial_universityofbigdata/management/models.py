from django.db import models
from django.utils import timezone, dateformat
from django.utils.translation import gettext_lazy as _

class ConfigBox(models.Model):
    name = models.CharField(max_length=32)
    max_submissions_per_day = models.IntegerField(default=3)
    authentication_code = models.CharField(
            max_length=20, default="XYZxyz095")  # issue #25
    auto_team_set_flag = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("config")
        verbose_name_plural = _("config")