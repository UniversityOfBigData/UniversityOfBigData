from django.db import models
from competitions.models import CompetitionModel
from django.utils.translation import gettext_lazy as _
from accounts.models import User
from accounts.models import TeamTag


def get_deleted_user():
    # ユーザーメールのハッシュ値を残したい
    return str(User.id)

def get_deleted_team():
    # idでも可
    return str(TeamTag.name)

class Discussion(models.Model):
    title_disc = models.CharField(max_length=128,blank=False, null=False, verbose_name=_('題名')) 
    post_tag_disc = models.ForeignKey(to=CompetitionModel, on_delete=models.CASCADE, related_name='discussion_post',verbose_name=_('コンペティション名'))
    added_datetime_disc = models.DateTimeField(_('投稿日'),auto_now_add=True)
    team_tag_disc = models.ForeignKey(to=TeamTag, on_delete=models.SET_NULL, related_name='discussion_team_tag',verbose_name=_('投稿チーム'),null=True)
    user_tag_disc = models.ForeignKey(to=User, on_delete=models.SET_NULL, related_name='discussion_user_tag',verbose_name=_('投稿者'),null=True)
    comment_field_disc = models.TextField(blank=False, null=False, verbose_name=_('コメント'))
    # 情報控え(ユーザーやチームが消えた時の処理用)
    author_user_nickname = models.CharField(max_length=64, blank=False, null=False, verbose_name=_('投稿者名'),default='anonymous user') 
    author_user_id = models.CharField(max_length=64, blank=False, null=False, verbose_name=_('投稿者ID'),default='0') 
    author_team_name = models.CharField(max_length=64, blank=False, null=False, verbose_name=_('投稿チーム'),default='anonymous term') 
    author_team_id = models.CharField(max_length=64, blank=False, null=False, verbose_name=_('投稿チームID'),default='0') 

    class Meta:
        verbose_name = _("DiscussionComment")
        verbose_name_plural = _("議論コメント")

    def __str__(self):
        return self.title_disc

    def save(self, *args, **kwargs):
        super(Discussion, self).save(*args, **kwargs)
        if (self.user_tag_disc):
            self.author_user_nickname = self.user_tag_disc.nickname
            self.author_user_id = self.user_tag_disc.id

        if (self.team_tag_disc):
            self.author_team_name = self.team_tag_disc.name
            self.author_team_id = self.team_tag_disc.id
        super(Discussion, self).save(*args, **kwargs)


class DiscussionPost(models.Model):
    post_tag_post = models.ForeignKey(to=Discussion, on_delete=models.CASCADE, related_name='discussion_post_tag',verbose_name=_('議論板'))
    added_datetime_post = models.DateTimeField(_('投稿日'),auto_now_add=True)
    team_tag_post = models.ForeignKey(to=TeamTag, on_delete=models.SET(get_deleted_team), related_name='post_team_tag',verbose_name=_('投稿チーム'),null=True)
    user_tag_post = models.ForeignKey(to=User, on_delete=models.SET(get_deleted_user), related_name='post_user_tag',verbose_name=_('投稿者'),null=True)
    comment_field_post = models.TextField(blank=False, null=False, verbose_name=_('コメント'))
    # 情報控え(ユーザーやチームが消えた時の処理用)
    author_user_nickname = models.CharField(max_length=64, blank=False, null=False, verbose_name=_('投稿者名'),default='anonymous user') 
    author_user_id = models.CharField(max_length=64, blank=False, null=False, verbose_name=_('投稿者ID'),default='0') 
    author_team_name = models.CharField(max_length=64, blank=False, null=False, verbose_name=_('投稿チーム'),default='anonymous term') 
    author_team_id = models.CharField(max_length=64, blank=False, null=False, verbose_name=_('投稿チームID'),default='0') 

    class Meta:
        verbose_name = _("Comment")
        verbose_name_plural = _("コメント")

    def __str__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        super(DiscussionPost, self).save(*args, **kwargs)
        if (self.user_tag_post):
            self.author_user_nickname = self.user_tag_post.nickname
            self.author_user_id = self.user_tag_post.id

        if (self.team_tag_post):
            self.author_team_name = self.team_tag_post.name
            self.author_team_id = self.team_tag_post.id
        super(DiscussionPost, self).save(*args, **kwargs)
