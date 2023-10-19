"""Test models."""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

from .models import TeamTag

User = get_user_model()


class UserModelTests(TestCase):
    """Userモデルのテスト."""

    def test_expected_user_model_class(self):
        """実装したUserクラスであるか."""
        from accounts.models import User as User_
        self.assertTrue(User is User_)

    def test_raise_IntegrityError_if_duplicated_username(self):
        """usernameの重複があるとIntegrityErrorを出すか."""
        User.objects.create(username='testuser')
        self.assertRaises(
                IntegrityError, User.objects.create,
                username='testuser')

    def test_raise_IntegrityError_if_duplicated_email(self):
        """emailの重複があるとIntegrityErrorを出すか."""
        User.objects.create(username='testuser1', email='hoge@example')
        self.assertRaises(
                IntegrityError, User.objects.create,
                username='testuser2', email='hoge@example')

    def test_raise_IntegrityError_if_duplicated_nickname(self):
        """nicknameの重複があるとIntegrityErrorを出すか."""
        User.objects.create(username='testuser1', nickname='hoge')
        self.assertRaises(
                IntegrityError, User.objects.create,
                username='testuser2', nickname='hoge')

    def test_empty_nickname_filled(self):
        """nicknameが空の場合にusernameと同じになっているか."""
        user = User.objects.create(
                username='testuser1', email='test1@test')
        self.assertEqual(user.nickname, 'testuser1')

        user = User.objects.create(
                username='testuser2', email='test2@test', nickname='')
        self.assertEqual(user.nickname, 'testuser2')

    def test_expected_initial_team_name(self):
        """selectedTeamの名前が想定通りか."""
        for i in range(1, 10):
            user = User.objects.create_user(
                    username=f'testuser{i}', email=f'test{i}@test')
            self.assertEqual(user.selectedTeam.name, f'InitialTeam{i}')

    def test_user_has_expected_permission(self):
        """通常ユーザの権限の確認."""
        user = User.objects.create_user(
                username='testuser', email='test@test')
        self.assertFalse(user.is_participant, False)
        self.assertFalse(user.is_staff, False)
        self.assertFalse(user.is_superuser, False)

    def test_staff_user_has_expected_permission(self):
        """スタッフユーザの権限の確認."""
        user = User.objects.create_staffuser(
                username='testuser', password='secret', email='test@test')
        self.assertTrue(user.is_participant, True)
        self.assertTrue(user.is_staff, True)
        self.assertFalse(user.is_superuser, False)

    def test_super_user_has_expected_permission(self):
        """スーパーユーザの権限の確認."""
        user = User.objects.create_superuser(
                username='testuser', password='secret', email='test@test')
        self.assertTrue(user.is_participant, True)
        self.assertTrue(user.is_staff, True)
        self.assertTrue(user.is_superuser, True)


class TeamTagTests(TestCase):
    """TeamTag のテスト."""

    def test_expected_member_data(self):
        """member_dataの値が想定通りか."""
        team_tag_name = 'test_team'
        team_tag = TeamTag(name=team_tag_name)
        team_tag.save(using='default')
        user_names = []
        for i in range(1, 10):
            user_name = f'testuser{i}'
            user = User.objects.create_user(
                    username=user_name, email=f'test{i}@test',
                    )
            user.team_tags.add(team_tag)
            team_tag.save()
            user_names.append(user_name)
            if i == 1:
                expected_member_data = f'{user_name},'
            else:
                expected_member_data = ','.join(user_names)
            self.assertEqual(team_tag.member_data, expected_member_data)
