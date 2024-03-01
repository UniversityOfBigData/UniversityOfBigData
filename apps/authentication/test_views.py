from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from parametrize import parametrize

from authentication.views import prepare_top_context

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
