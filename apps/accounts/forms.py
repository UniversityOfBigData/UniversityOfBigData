from django.utils.translation import gettext_lazy as _
from django import forms
from .models import User, TeamTag

class SetProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SetProfileForm, self).__init__(*args, **kwargs)
        
        for field in self.fields.values():  # bootstrapで使用するform-controlクラス
            field.widget.attrs['class'] = 'form-control'
        
    class Meta:
        User.is_guest = True
        model = User
        fields = ('username',
        'email',
        'nickname',
        'affiliation_organization',
        'password',
        )
        help_texts = {
            'username': _('入力例：「bigdata001」。英数字で入力してください。'),
            'email': _('gmail アドレス'),
            'nickname': _('コンペティションで使用するニックネームを入力してください。ニックネームは本サイト上で公開されます。<br>英数字でお願いします。登録後に変更可能です。'),
            'affiliation_organization': _('所属など　入力例：「ビッグデータ大学」。公開はされません'),
            'password': _('パスワード'),
        }

class ProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        
        for field in self.fields.values():  # bootstrapで使用するform-controlクラス
            field.widget.attrs['class'] = 'form-control'
        
    class Meta:
        User.is_guest = True
        model = User
        fields = ('username',
        'email',
        'nickname',
        'student_number',
        'affiliation_organization',
        )
        help_texts = {
            'username': _('入力例：「bigdata001」。英数字で入力してください。'),
            'email': _('gmail アドレス'),
            'nickname': _('コンペティションで使用するニックネームを入力してください。ニックネームは本サイト上で公開されます。<br>英数字でお願いします。登録後に変更可能です。'),
            'student_number': _('学籍番号'),
            'affiliation_organization': _('所属など　入力例：「ビッグデータ大学」。公開はされません'),
        }
