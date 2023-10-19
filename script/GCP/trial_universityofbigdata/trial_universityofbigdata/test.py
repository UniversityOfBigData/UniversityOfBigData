"""Tests for the application."""

import unittest
from django.conf import settings


class SettingTest(unittest.TestCase):
    """アプリのsettingsに関するテスト."""

    def test_secret_key_assigned(self):
        """SECRET_KEYに環境変数DJANGO_SECRET_KEYの値が代入されていることを確認."""
        self.assertEqual(
                settings.SECRET_KEY,
                'django-insecure-test-secret-key')

    def test_google_oauth2_keysecret(self):
        """Google OAuth2のKEYとSECRETの値が環境変数から代入されていることを確認."""
        self.assertEqual(
                settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
                'google-oauth2-test-key')
        self.assertEqual(
                settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
                'google-oauth2-test-secret')
