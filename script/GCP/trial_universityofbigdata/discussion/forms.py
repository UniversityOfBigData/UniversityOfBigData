from django import forms
from .models import Discussion, DiscussionPost

class DiscussionCreateForm(forms.ModelForm):
    """
    投稿フォーム
    """
    class Meta:
        model = Discussion
        fields = ('title_disc',
                  'comment_field_disc',)

class DiscussionPostCreateForm(forms.ModelForm):
    """
    投稿フォーム
    """
    class Meta:
        model = DiscussionPost
        fields = ('comment_field_post',)

