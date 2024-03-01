from django.contrib import admin
from .models import Discussion
from .models import DiscussionPost

class DiscussionAdmin(admin.ModelAdmin):
    list_display = ('id','title_disc','post_tag_disc','added_datetime_disc','team_tag_disc','user_tag_disc','comment_field_disc',)
    fields = ('id','title_disc','post_tag_disc','added_datetime_disc','team_tag_disc','user_tag_disc','comment_field_disc',)
    readonly_fields = ('id','added_datetime_disc', )

admin.site.register(Discussion, DiscussionAdmin)

class DiscussionPostAdmin(admin.ModelAdmin):
    list_display = ('id','post_tag_post','added_datetime_post','team_tag_post','user_tag_post','comment_field_post',)
    fields = ('id','post_tag_post','added_datetime_post','team_tag_post','user_tag_post','comment_field_post',)
    readonly_fields = ('id','added_datetime_post', )

admin.site.register(DiscussionPost, DiscussionPostAdmin)
