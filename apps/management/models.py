from django.db import models
from django.utils import timezone, dateformat
from django.utils.translation import gettext_lazy as _

class ConfigBox(models.Model):
    authentication_code = models.CharField(
            max_length=20, default="XYZxyz095")  # issue #25
    class Meta:
        verbose_name = _("参加認証コード")
        verbose_name_plural = _("参加認証コード")
