"""Test views."""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


def _create_test_user():
    return User.objects.create_user(
            username='testuser1', password='secret1',
            )


class ProfileEditViewTests(TestCase):
    """プロファイル編集ページのテスト.

    - ログイン必須
    """

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("profileedit")
        cls.test_user1 = _create_test_user()

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_200_if_logged_in(self):
        self.client.force_login(self.test_user1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


class ProfileRegistrationViewTests(TestCase):
    """プロファイル登録ページのテスト.

    - ログイン不要
    """

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("signup")
        cls.test_user1 = _create_test_user()

    def test_200_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_200_if_logged_in(self):
        self.client.force_login(self.test_user1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


class ProfileRegistrationGoogleViewTests(TestCase):
    """Google OAuth2 による認証で登録するページのテスト."""

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("signup_google")
        cls.test_user1 = _create_test_user()

    def test_302_if_not_logged_in(self):
        """ログインしていないとリダイレクトされる.

        NOTE: この挙動で良いか要確認
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_200_if_logged_in(self):
        self.client.force_login(self.test_user1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


class SuspensionUsersViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("suspension_users")
        cls.test_user1 = _create_test_user()

    def test_302_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_200_if_logged_in(self):
        self.client.force_login(self.test_user1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


class RegistrationUsersViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("registration_users")
        cls.test_user1 = _create_test_user()

    def test_302_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_200_if_logged_in(self):
        self.client.force_login(self.test_user1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


class ManageTeamsViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("manage_teams")
        cls.test_user1 = _create_test_user()

    def test_302_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_200_if_logged_in(self):
        self.client.force_login(self.test_user1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


class MakeTeamsViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("make_team")
        cls.test_user1 = _create_test_user()

    def test_302_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_200_if_logged_in(self):
        self.client.force_login(self.test_user1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


class CertificationTeamsViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("certification_teams")
        cls.test_user1 = _create_test_user()

    def test_302_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_200_if_logged_in(self):
        self.client.force_login(self.test_user1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
