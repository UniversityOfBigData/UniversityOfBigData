from django.contrib import admin
from .models import ConfigBox


class ConfigBoxAdmin(admin.ModelAdmin):
    # リスト画面
    list_display = (
            'id',
            )

    # 以下の2行は詳細画面のため
    fields = (
            'id',
            'authentication_code',
            )
    readonly_fields = ('id',)


admin.site.register(ConfigBox, ConfigBoxAdmin)
