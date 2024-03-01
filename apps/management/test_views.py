from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import ConfigBox

User = get_user_model()

class EditConfigBoxViewTest(TestCase):
    """招待コード設定のテスト."""

    @classmethod
    def setUpTestData(cls):
        cls.orig_code = 'orig_code'
        cls.new_code = 'new_code'
        # テスト用ユーザ登録
        cls.test_user1 = User.objects.create_user(
                username='testuser1', password='password1', email='test1@test'
                )
        cls.test_user1.save()
        cls.test_staffuser1 = User.objects.create_staffuser(
                username='test_staffuser1', password='password1', email='test_staff1@test'
                )
        cls.test_staffuser1.save()
        cls.test_superuser1 = User.objects.create_staffuser(
                username='test_superuser1', password='password1', email='test_super1@test'
                )
        cls.test_superuser1.save()

    def setUp(self):
        # ConfigBoxの作成
        self.cfg = ConfigBox.objects.create(
                authentication_code=self.orig_code,
                )

    def test_update_authentication_code_by_superuser(self):
        """スーパーユーザが認証コードを変更できる."""
        self.client.force_login(self.test_superuser1)
        response = self.client.post(
                reverse('edit_config', args=[1]),
                {
                    'authentication_code': self.new_code,
                })
        cfg = ConfigBox.objects.get(id=1)
        self.assertEqual(cfg.authentication_code, self.new_code)

    def test_update_authentication_code_by_staffuser(self):
        """スタッフユーザが認証コードを変更できる."""
        self.client.force_login(self.test_staffuser1)
        response = self.client.post(
                reverse('edit_config', args=[1]),
                {
                    'authentication_code': self.new_code,
                })
        cfg = ConfigBox.objects.get(id=1)
        self.assertEqual(cfg.authentication_code, self.new_code)

    def test_update_authentication_code_by_participant(self):
        """一般ユーザは認証コードを変更できない, ステータスコードは403."""
        self.client.force_login(self.test_user1)
        response = self.client.post(
                reverse('edit_config', args=[1]),
                {
                    'authentication_code': self.new_code,
                })
        self.assertEqual(response.status_code, 403)
        cfg = ConfigBox.objects.get(id=1)
        self.assertEqual(cfg.authentication_code, self.orig_code)

    def test_update_authentication_code_by_anon(self):
        """非ログインユーザは認証コードを変更できない, ステータスコードは302."""
        response = self.client.post(
                reverse('edit_config', args=[1]),
                {
                    'authentication_code': self.new_code,
                })
        self.assertEqual(response.status_code, 302)
        cfg = ConfigBox.objects.get(id=1)
        self.assertEqual(cfg.authentication_code, self.orig_code)


