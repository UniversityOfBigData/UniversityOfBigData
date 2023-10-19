from django.contrib import admin
from .models import ConfigBox


class ConfigBoxAdmin(admin.ModelAdmin):
    # リスト画面
    list_display = ('id','name',)

    # 以下の2行は詳細画面のため
    fields = (  'id','name',
                #'max_submissions_per_day',
                'authentication_code',
                'auto_team_set_flag',
              )
    readonly_fields = ('id',)

admin.site.register(ConfigBox, ConfigBoxAdmin)