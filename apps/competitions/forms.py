from django import forms
from .models import CompetitionModel, CompetitionPost
from django.utils.translation import gettext_lazy as _


class EditCompetitionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EditCompetitionForm, self).__init__(*args, **kwargs)

        for field in self.fields.values():  # bootstrapで使用するform-controlクラス
            field.widget.attrs['class'] = 'form-control'

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
        )
        help_texts = {
            'title': _('コンペティションのタイトル（日本語）'),
            'title_en': _('コンペティションのタイトル（英語）(optional)'),
            'owner': _('コンペティション主催者'),
            'competition_abstract': _('コンペティションの概要（日本語）'),
            'competition_abstract_en': _('コンペティションの概要（英語）(optional)'),
            'competition_description': _('コンペティションの説明（日本語）'),
            'competition_description_en': _('コンペティションの説明（英語）(optional)'),
            'problem_type': _('問題の種類'),
            'evaluation_type': _('評価指標'),
            'leaderboard_type': _('リーダーボードの種類'),
            'use_forum': _('フォーラムの使用'),
            'open_datetime': _('コンペティション開始日'),
            'close_datetime': _('コンペティション終了日'),
            'public': _('公開設定'),
            'invitation_only': _('参加者制限'),
            'n_max_submissions_per_day': _('１日の最大投稿回数'),
            'public_leaderboard_percentage': _('中間評価に使うデータの割合'),
            'blob_key': _('予測用データファイル'),
            'truth_blob_key': _('正解データファイル'),
            'file_description': _('ファイルの説明（日本語）'),
            'file_description_en': _('ファイルの説明（英語）(optional)'),
        }


class CompetitionPostChangeForm(forms.ModelForm):
    """投稿フォーム."""

    def __init__(self, *args, **kwargs):
        super(CompetitionPostChangeForm, self).__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = CompetitionPost
        fields = (
                'post',
                'team_tag',
                'user_tag',
                'post_key',
                'count_par_today',
                )

class CompetitionPostCreateForm(forms.ModelForm):
    """投稿フォーム."""

    def __init__(self, *args, **kwargs):
        super(CompetitionPostCreateForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = CompetitionPost
        fields = ('post_key',)

    def clean_post_key(self):
        file = self.cleaned_data.get('post_key')
        if not file.name.endswith('.csv'):
            self.add_error('post_key', _('拡張子はcsvのみです'))
        return file
