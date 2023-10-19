from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from parametrize import parametrize

from universityofbigdata.views import (
        top, prepare_top_context, prepare_login_required_context,
        )

User = get_user_model()


class TopPageViewTests(TestCase):
    """トップページのテスト."""

    @parametrize(
            'num_users',
            [
                (0, ),
                (1, ),
                (2, ),
            ])
    def test_expected_context(self, num_users):
        """トップページのコンテキストが期待する値になっているか."""
        for i in range(num_users):
            user = User.objects.create_user(
                username=f'testuser{i}', password='password1',
                email=f'test{i}@test'
                )
            user.save()
        response = self.client.get(reverse('top'))
        request = response.wsgi_request
        context = prepare_top_context(request)

        self.assertEqual(context['users_num'], num_users)
        self.assertEqual(len(context['CurrentCompetitions_box']), 0)
        self.assertEqual(len(context['ComingCompetitions_box']), 0)
        self.assertEqual(context['publicCompetition_num'], 0)
        self.assertEqual(context['closedCompetition_num'], 0)



# login_requiredは機能していないと思われるのでテストなし
#class LoginRequiredTest(TestCase):
#    """login_requiredのテスト."""
#
#    @classmethod
#    def setUpTestData(cls):
#        # ConfigBoxの作成
#        ConfigBox.objects.create(name='signInCode')
#
#        # テスト用ユーザ登録
#        cls.test_user1 = User.objects.create(
#                username='testuser1', password='password1',
#                )
#        cls.test_user1.save()
#
#    def test_get_without_login(self):
#        response = self.client.get(reverse('login_required'))
#        request = response.wsgi_request
#        context = prepare_login_required_context(request)
#
#    def test_get_with_login(self):
#        self.client.force_login(self.test_user1)
#        response = self.client.get(reverse('login_required'))
#        request = response.wsgi_request
#        context = prepare_login_required_context(request)
#
#    def test_post_correct_code_without_login(self):
#        response = self.client.post(reverse('login_required'), {'invitation_code': 'XYZxyz095'})
#        request = response.wsgi_request
#        context = prepare_login_required_context(request)
#
#    def test_post_wrong_code_without_login(self):
#        response = self.client.post(reverse('login_required'), {'invitation_code': 'wrong_code'})
#        request = response.wsgi_request
#        context = prepare_login_required_context(request)
#
#    def test_post_with_login(self):
#        self.client.force_login(self.test_user1)
#        response = self.client.post(reverse('login_required'))
#        request = response.wsgi_request
#        context = prepare_login_required_context(request)
