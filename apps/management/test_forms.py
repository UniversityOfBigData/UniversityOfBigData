"""Test forms."""

from django.test import TestCase
from django.contrib.auth import get_user_model

from accounts.models import User, TeamTag
from .forms import CertificationTeamsForm, ManageUsersForm

class CertificationTeamsFormTests(TestCase):
    """CertificationTeamsForm のテスト."""

    def test_valid_when_unicode_name(self):
        params = {
            'name': '日本語の名前',
        }
        team_tag = TeamTag.objects.create(name='test_team')
        form = CertificationTeamsForm(params, instance=team_tag)
        self.assertTrue(form.is_valid())
        self.assertFalse(form.has_error('name'))
        
class ManageUsersFormTests(TestCase):
    """ManageUsersForm のテスト."""

    def test_invalid_if_unicode_username(self):
        params = {
            'username': '日本語の名前',
            'email': '',
            'nickname': '',
            'is_participant': True,
            'is_active': True,
        }
        user = User.objects.create_user(
            username='test_user', email='test@test',
        )
        form = ManageUsersForm(params, instance=user)
        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error('username'))
        
