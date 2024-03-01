from django.db import models
from accounts.models import User
from accounts.models import TeamTag
from django.utils.translation import gettext_lazy as _
import datetime
from django.utils import timezone
import uuid
from typing import Tuple
from numbers import Real

from static.lib import metrics


def savePredictionPath(instance, filename):
    ext = filename.split('.')[-1]
    new_name = instance.title + "_data"
    return f'competition/{instance.uuid}/data/{new_name}.{ext}'


def saveGroundTruthPath(instance, filename):
    ext = filename.split('.')[-1]
    new_name = instance.title + "_truthData"
    return f'competition/{instance.uuid}/data/{new_name}.{ext}'


def saveSubmissionPath(instance, filename):
    ext = filename.split('.')[-1]
    team_name = instance.team_tag.name if instance.team_tag else 'unknown-team'
    user_nickname = instance.user_tag.nickname \
        if instance.user_tag else 'unknown-user'
    new_name = team_name + "_" + user_nickname + "_Post"
    date_text = datetime.date.today()
    date_text = str(date_text)
    date_text = date_text.replace('-','')
    post_count=instance.count_par_today # 同一チームで本日何個投稿しているか？のカウント
    return f'competition/{instance.post.uuid}/{date_text}/{new_name}_{post_count}.{ext}'


def get_deleted_owner():
    return str(User.id)


def get_deleted_winner():
    return str(TeamTag.name)


class CompetitionModel(models.Model):
    title = models.CharField(
            _('コンペティションのタイトル（日本語）'),
            max_length=150, blank=False)
    title_en = models.CharField(
            _('コンペティションのタイトル（英語）(optional)'),
            max_length=150, blank=True, null=True)
    owner = models.ForeignKey(
            to=User, on_delete=models.SET_NULL, related_name='owner',
            verbose_name=_('主催者'), blank=True, null=True)
    owner_name = models.CharField(
            _('主催者名(控え)'), max_length=64,
            blank=False, null=False, default='owner')
    competition_abstract = models.TextField(
            _('コンペティションの概要（日本語）'), blank=False)
    competition_abstract_en = models.TextField(
            _('コンペティションの概要（英語）(optional)'),
            blank=True, null=True)
    competition_description = models.TextField(
            _('コンペティションの説明（日本語）'), blank=False)
    competition_description_en = models.TextField(
            _('コンペティションの説明（英語）(optional)'),
            blank=True, null=True)
    problem_type = models.CharField(
            _('問題の種類'), max_length=50, default='regression',
            choices=[('regression', _('回帰')), ('classification', _('分類')), ])
    evaluation_type = models.CharField(
            _('評価指標'), max_length=50, default='',
            choices=[(k, v.display_name) for k, v in metrics.items()])
    leaderboard_type = models.CharField(
            _('リーダーボードの種類'), max_length=50, default='default',
            choices=[('default', _('標準')), ])
    use_forum = models.BooleanField(
            _('フォーラムの使用'), default=False)  # 不要？
    added_datetime = models.DateTimeField(
            _('コンペティション登録日'), auto_now_add=True)  # 非表示
    open_datetime = models.DateTimeField(_('コンペティション開始日'),)
    close_datetime = models.DateTimeField(_('コンペティション終了日'),)

    # 公開参加制限の有無
    public = models.BooleanField(_('公開設定'), default=True)
    invitation_only = models.BooleanField(_('参加者制限'), default=False)
    n_max_submissions_per_day = models.IntegerField(
            _('１日の最大投稿回数'), default=3)

    # 評価指標と投稿ファイルフォーマット
    public_leaderboard_percentage = models.IntegerField(
            _('中間評価に使うデータの割合'), default=50)
    blob_key = models.FileField(_('予測用データファイル'), upload_to=savePredictionPath)
    truth_blob_key = models.FileField(_('正解データファイル'), upload_to=saveGroundTruthPath)
    file_description = models.TextField(_('ファイルの説明（日本語）'), blank=False)
    file_description_en = models.TextField(
            _('ファイルの説明（英語）(optional)'), blank=True, null=True)

    # 日時で自動設定
    status = models.CharField(
            _('状態'), max_length=50, default='coming',
            choices=[
                ('coming', _('開催準備中')),
                ('active', _('開催中')),
                ('completed', _('開催終了')),
                ])  # 非表示、内部状態
    # 数の保持
    n_participants = models.IntegerField(_('参加者数'), default=0)  # 参加者数
    n_teams = models.IntegerField(_('参加チーム数'), default=0)  # 参加チーム数
    n_submissions = models.IntegerField(_('承認数'), default=0)  # 承認数
    n_posts = models.IntegerField(_('投稿数'), default=0)  # 投稿数
    # 参加認証
    authentication_code = models.CharField(
            _('認証コード'), max_length=30, default='', blank=True, null=True)
    submissions_teams = models.ManyToManyField(TeamTag)
    # 優勝者
    winner_teams = models.ManyToManyField(
            to=TeamTag, related_name='winner_team',
            verbose_name=_('優勝チーム'), blank=True)

    uuid = models.UUIDField(
            primary_key=False, default=uuid.uuid4, editable=False)

    # スコア
    displayed_decimal_places = models.IntegerField(
            _('表示されるスコアの小数点以下の桁数'), default=5,
            blank=True)  # 投稿数

    class Meta:
        verbose_name = _("コンペティション")
        verbose_name_plural = _("コンペティション")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if (self.owner):
            self.owner_name = self.owner.nickname
        else:
            self.owner_name = 'owner lost'
        super(CompetitionModel, self).save(*args, **kwargs)

    @property
    def greater_score_is_better(self):
        return metrics[self.evaluation_type].greater_is_better

    def evaluate_submission(
            self, submission_file_path: str) -> Tuple[Real, Real]:
        """Public LBおよびPrivate LBの評価指標を返す."""
        return metrics[self.evaluation_type](
                self.public_leaderboard_percentage / 100
                )(self.truth_blob_key, submission_file_path)

    def displayed_score(self, score: models.DecimalField) -> str:
        return (
                '{' + f':.{self.displayed_decimal_places}f' + '}'
                ).format(score)


def get_deleted_user():
    return str(User.id)

def get_deleted_team():
    return str(TeamTag.name)


class CompetitionPost(models.Model):
    post = models.ForeignKey(
            to=CompetitionModel, on_delete=models.CASCADE,
            related_name='posts', verbose_name=_('コンペティション名'))
    added_datetime = models.DateTimeField(_('投稿日'), auto_now_add=True)
    team_tag = models.ForeignKey(
            to=TeamTag, on_delete=models.SET_NULL, related_name='team_tag',
            verbose_name=_('投稿チーム'), null=True)
    user_tag = models.ForeignKey(
            to=User, on_delete=models.SET_NULL, related_name='user_tag',
            verbose_name=_('投稿者'), null=True)
    post_key = models.FileField(
            _('投稿データファイル'), upload_to=saveSubmissionPath,)
    poster = models.CharField(_('投稿者名'), max_length=50)
    poster_id = models.CharField(_('投稿者ID'), max_length=50, default='0')
    team = models.CharField(_('チーム名'), max_length=50)
    team_id = models.CharField(_('チームID'), max_length=50, default='0')
    count_par_today = models.IntegerField(_('この日の投稿回数'), default=0)
    count_posts = models.IntegerField(_('チームの総投稿回数'), default=0)
    intermediate_score = models.DecimalField(
            _('中間スコア'), max_digits=15, decimal_places=8, default=0.0)
    final_score = models.DecimalField(
            _('最終スコア'), max_digits=15, decimal_places=8, default=0.0)

    def __str__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        if(self.user_tag):
            self.poster = self.user_tag.nickname
            self.poster_id = str(self.user_tag.id)
        if(self.team_tag):
            self.team = self.team_tag.name
            self.team_id = str(self.team_tag.id)

        # FIXME: 下記方法による投稿数取得はスレッドセーフではないと思われる

        # 同一チームタグの総投稿数
        query_set = CompetitionPost.objects.filter(
                post=self.post, team_tag=self.team_tag, )
        self.count_posts = len(query_set) + 1

        # 同一チームタグの本日の総投稿数
        today = timezone.localtime(timezone.now()).date()
        today = timezone.datetime(
                today.year, today.month, today.day,
                tzinfo=timezone.get_current_timezone())
        tomorrow = (today + datetime.timedelta(days=1))
        query_set = CompetitionPost.objects.filter(
                post=self.post, team_tag=self.team_tag,
                added_datetime__range=[today, tomorrow])
        self.count_par_today = len(query_set) + 1

        super(CompetitionPost, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _("コンペティション投稿データ")
        verbose_name_plural = _("コンペティション投稿データ")
        unique_together = ['id']
