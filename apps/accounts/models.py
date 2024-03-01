from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.db import Error
from django.http import Http404
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import logging


class UserManager(BaseUserManager):
    """ユーザ管理クラス."""

    use_in_migrations = True

    def _set_user(self, username, password, **extra_fields):
        try:
            username = self.model.normalize_username(username)
            user = self.model(username=username, **extra_fields)
            user.set_password(password)
            user.save(using=self.db)
            return user
        except Error:
            # NOTE: User作成時の例外はusername, email, nicknameの重複がある場合のみ
            #       実装されているため下記のようなエラーメッセージを出している.
            raise Http404(
                    "User make Error. User with similar parameters exists.")

    def _create_user(self, username, password, **extra_fields):
        user = self._set_user(username, password, **extra_fields)

        # 初期チームの割り当て
        # チームのセット (1人1チームの時の設定)
        team_set = TeamTag.objects.all()
        team_count = len(team_set) + 1
        initial_team_name = 'InitialTeam'+str(team_count)

        def check_is_team(initial_team_name):
            """チームに未所属の場合 Trueを返す."""
            q = TeamTag.objects.filter(name=initial_team_name)
            return (q.first() is None)

        # チーム名の重複回避処理
        if not (check_is_team(initial_team_name)):
            addstr = ''
            while True:
                addstr = addstr + 'X'
                initial_team_name = 'InitialTeam'+addstr+str(team_count)
                if check_is_team(initial_team_name):
                    break
        part_obj = TeamTag.objects.create(name=initial_team_name)  # チーム生成
        user.selectedTeam = part_obj

        user.save(using=self.db)
        # ログのセット
        logger = logging.getLogger(__name__)
        logger.info('make user'+str(username))
        return user

    def create_user(self, username, password=None, **extra_fields):
        """一般ユーザの作成."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, password, **extra_fields)

    def create_staffuser(self, username, password, **extra_fields):
        """スタッフユーザの作成."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_participant', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('is_staff=Trueである必要があります。'))
        if extra_fields.get('is_participant') is not True:
            raise ValueError(_('is_participant=Trueである必要があります。'))
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        """スーパーユーザの作成."""
        extra_fields.setdefault('nickname', username)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_participant', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('is_staff=Trueである必要があります。'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('is_superuser=Trueである必要があります。'))
        if extra_fields.get('is_participant') is not True:
            raise ValueError(_('is_participant=Trueである必要があります。'))
        return self._create_user(username, password, **extra_fields)


class TeamTag(models.Model):
    """チームタグのモデル."""

    name = models.CharField(max_length=32, 
                            unique=True,
                            null=True,
                            error_messages={
                                'unique': _("A team with that team name already exists."),})
    logs_data = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = _("チーム")
        verbose_name_plural = _("チーム")

    # ここから追加 save時の自動対応 処理を追加
    def save(self, *args, **kwargs):
        """保存時に現在同タグが付与されているメンバーを更新する."""
        super(TeamTag, self).save(*args, **kwargs)
        # 処理 現在メンバー更新処理
        return self
    # ここまでを追加

    def __str__(self):
        return self.name


class User(PermissionsMixin, AbstractBaseUser):
    """ユーザのモデル."""

    username_validator = ASCIIUsernameValidator()
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        }
    )
    email = models.EmailField(
        _('gmail address'),
        unique=True,
        blank=False,
        error_messages={
            'unique': _("A user with that email already exists."),
            }
        )
    nickname = models.CharField(
            _('nickname'),
            max_length=150,
            unique=True,
            validators=[username_validator],
            error_messages={
                'unique': _("A user with that nickname already exists."),
            }
    )
    # 個人確認用オプション
    affiliation_organization = models.CharField(
            _('affiliation organization'),
            max_length=150, blank=True)  # 大学名・企業名

    # 学籍番号
    student_number = models.CharField(
        _('student number'),
        max_length=150, blank=True)
    
    # チーム機能
    selectedTeam = models.ForeignKey(
        to=TeamTag, on_delete=models.CASCADE,
        related_name='selected_team', null=True)  # メイン所属チーム

    # 権限のコード
    invitation_code = models.CharField(
            _('invitation code'),
            max_length=50, blank=True)  # 招待コード
    # 権限
    is_admin = models.BooleanField(_('admin'), default=False)
    is_staff = models.BooleanField(_('staff'), default=False)
    is_guest = models.BooleanField(_('guest'), default=True)  # ユーザー生成段階の権限
    is_participant = models.BooleanField(
            _('participant'), default=False)  # 参加者になった時の権限
    is_active = models.BooleanField(_('active'), default=True)

    # 日時
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()
    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        db_table = 'users'
        swappable = 'AUTH_USER_MODEL'

    def email_user(self, subject, message, from_email=None, **kwargs):
        """ユーザへのメール送信."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        """ユーザモデルの保存."""
        # セーブ時にnicknameが空欄の場合、usernameで埋める
        if(self.nickname is None or self.nickname == ""):
            self.nickname = self.username
        return super(User, self).save(*args, **kwargs)
