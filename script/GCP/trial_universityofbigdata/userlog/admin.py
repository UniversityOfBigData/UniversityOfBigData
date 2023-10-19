from django.contrib import admin
from .models import LogBox, ManagementLogBox

# Register your models here.
class LogBoxAdmin(admin.ModelAdmin):
    # リスト画面
    list_display = ('id','name',)

    # 以下の2行は詳細画面のため
    fields = (  'id',
                'name',
                'log_field',
              )
    readonly_fields = ('id','name',)

admin.site.register(LogBox, LogBoxAdmin)

class ManagementLogBoxAdmin(admin.ModelAdmin):
    # リスト画面
    list_display = ('id','name',)

    # 以下の2行は詳細画面のため
    fields = (  'id',
                'name',
                'log_field',
              )
    readonly_fields = ('id','name',)

admin.site.register(ManagementLogBox, ManagementLogBoxAdmin)