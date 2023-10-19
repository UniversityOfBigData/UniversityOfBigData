from django.db import models
from django.utils import timezone, dateformat
from django.utils.translation import gettext_lazy as _
# Create your models here.
class LogBox(models.Model):
    name = models.CharField(max_length=32)
    log_field = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = _("log_box")
        verbose_name_plural = _("log_box")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not (self.id):
            self.name = dateformat.format(
                    timezone.localtime(timezone.now()), 'Y-m-d')
        return super(LogBox, self).save(*args, **kwargs)


class ManagementLogBox(models.Model):
    name = models.CharField(max_length=32)
    log_field = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = _("management_log_box")
        verbose_name_plural = _("management_log_box")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not(self.id):
            self.name = _('management_log')
            self.log_field = str({
                'time': '2022-12-16 23:30:00',
                'massage': 'ビッグデータ大学',
                'ids': '1'
                })
        return super(ManagementLogBox, self).save(*args, **kwargs)
    

def get_log_box():
    time = dateformat.format(timezone.localtime(timezone.now()), 'Y-m-d')
    try:
        my_object = LogBox.objects.get(name=time)
        return my_object
    except LogBox.DoesNotExist:
        my_object = LogBox.objects.create(name=time)
        return my_object
    
def get_mlog_box():
    name = 'management_log'
    try:
        my_object = ManagementLogBox.objects.get(name=name)
        return my_object
    except ManagementLogBox.DoesNotExist:
        my_object = ManagementLogBox.objects.create(name=name)
        return my_object