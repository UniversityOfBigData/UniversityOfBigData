from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import ConfigBox
from accounts.models import User, TeamTag
from competitions.models import CompetitionModel

class CompetitionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        fields_box=[
            'title',
            'title_en',
            'owner',
            'competition_abstract',
            'competition_abstract_en',
            'competition_description',
            'competition_description_en',
            'problem_type',
            'evaluation_type',
            'leaderboard_type',
            'n_max_submissions_per_day',
            'public_leaderboard_percentage',
            'blob_key',
            'truth_blob_key',
            'file_description',
            'file_description_en',
            'displayed_decimal_places',
        ]
        for f in fields_box:
            self.fields[f].widget.attrs['class'] = 'form-control'
        self.fields['open_datetime'].widget = forms.DateTimeInput(
            attrs={"type": "datetime-local", "value": timezone.datetime.now()})
        self.fields['open_datetime'].input_formats = ['%Y-%m-%dT%H:%M']
        self.fields['close_datetime'].widget = forms.DateTimeInput(
            attrs={"type": "datetime-local", "value": timezone.datetime.now()})
        self.fields['close_datetime'].input_formats = ['%Y-%m-%dT%H:%M']

    class Meta:
        model = CompetitionModel
        fields = (
            'title',
            'title_en',
            'owner',
            'competition_abstract',
            'competition_abstract_en',
            'competition_description',
            'competition_description_en',
            'problem_type',
            'evaluation_type',
            'leaderboard_type',
            'use_forum',
            'open_datetime',
            'close_datetime',
            'public',
            'invitation_only',
            'n_max_submissions_per_day',
            'public_leaderboard_percentage',
            'blob_key',
            'truth_blob_key',
            'file_description',
            'file_description_en',
            'displayed_decimal_places',
        )
        help_texts = {
            'title': _('コンペティションのタイトル（日本語）'),
            'title_en': _('コンペティションのタイトル（英語）(optional)'),
            'owner': _('コンペティション主催者'),
            'competition_abstract': _('コンペティションの概要（日本語）'),
            'competition_abstract_en' : _('コンペティションの概要（英語）(optional)'),
            'competition_description' : _('コンペティションの説明（日本語）'),
            'competition_description_en' : _('コンペティションの説明（英語）(optional)'),
            'problem_type' : _('問題の種類'),
            'evaluation_type': _('評価指標'),
            'leaderboard_type': _('リーダーボードの種類'),
            'use_forum': _('フォーラムの使用'),
            'open_datetime': _('コンペティション開始日'),
            'close_datetime': _('コンペティション終了日'),
            'public' : _('公開設定'),
            'invitation_only' : _('参加者制限'),
            'n_max_submissions_per_day' : _('１日の最大投稿回数'),
            'public_leaderboard_percentage': _('中間評価に使うデータの割合'),
            'blob_key': _('予測用データファイル'),
            'truth_blob_key': _('正解データファイル'),
            'file_description': _('ファイルの説明（日本語）'),
            'file_description_en': _('ファイルの説明（英語）(optional)'),
            'displayed_decimal_places': _('スコア表示の小数点以下の桁数'),
        }
        
class CertificationTeamsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CertificationTeamsForm, self).__init__(*args, **kwargs)
        
        for field in self.fields.values():  # bootstrapで使用するform-controlクラス
            field.widget.attrs['class'] = 'form-control'
        
    class Meta:
        User.is_guest = True
        model = TeamTag
        fields = (
            'name',
        )
        help_texts = {
            'name': _('チーム名'),
        }

class MakeTeamForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MakeTeamForm, self).__init__(*args, **kwargs)

        for field in self.fields.values():  # bootstrapで使用するform-controlクラス
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        User.is_guest = True
        model = TeamTag
        fields = (
        'name',
        )
        help_texts = {
            'name': _('チーム名'),
        }


class ManageUsersForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ManageUsersForm, self).__init__(*args, **kwargs)

        for field in self.fields.values():  # bootstrapで使用するform-controlクラス
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        User.is_guest = True
        model = User
        fields = (
                'username',
                'email',
                'nickname',
                'is_participant',
                'is_active',
                )
        help_texts = {
                'username': _('入力例：「bigdata001」。英数字で入力してください。'),
                'email': _('gmail アドレス'),
                'nickname': _(
                    'コンペティションで使用するニックネームを英数字で入力してください。'
                    'ニックネームは本サイト上で公開されます。<br>ニックネームは登録後に変更可能です。'),
                'is_participant': _('参加者権限'),
                'is_active': _('有効/無効'),
                }


class EditConfigBoxForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EditConfigBoxForm, self).__init__(*args, **kwargs)
        self.fields['authentication_code'].widget.attrs['class'] = 'form-control'

    class Meta:
        model = ConfigBox
        fields = (
                'authentication_code',
        )
        help_texts = {
                'authentication_code': _('参加認証コード'),
        }
