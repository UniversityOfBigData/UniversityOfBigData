"""Test forms."""

from django.test import TestCase
from django.contrib.auth import get_user_model

from .forms import (
        ProfileForm,
        SetProfileForm,
    )
from .models import TeamTag


User = get_user_model()


class SetProfileFormTests(TestCase):
    """SetProfileForm のテスト."""

    def test_invalid_if_unicode_username(self):
        params = {
            'username': '日本語の名前',
            'email': '',
            'nickname': '',
            'affiliation_organization': '',
            'password': '',
        }
        user = User.objects.create_user(
            username='test_user', email='test@test',
        )
        form = SetProfileForm(params, instance=user)
        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error('username'))


class ProfileFormTests(TestCase):
    """ProfileForm のテスト."""

    def test_invalid_if_unicode_username(self):
        params = {
            'username': '日本語の名前',
            'email': '',
            'nickname': '',
            'affiliation_organization': '',
            'password': '',
        }
        user = User.objects.create_user(
            username='test_user', email='test@test',
        )
        form = ProfileForm(params, instance=user)
        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error('username'))






