from django import forms
from django.utils.translation import gettext_lazy as _

class login_requiredForm(forms.Form):
    invitation_code = forms.CharField()

