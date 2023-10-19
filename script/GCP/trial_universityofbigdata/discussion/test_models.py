"""Test models."""

from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()

from .models import (
    Discussion, DiscussionPost, 
    )
from competitions.test_views import launch_competition
from accounts.models import TeamTag


def _create_thread(
        user, compe, team, title, comment):
    return Discussion(
        title_disc=title,
        post_tag_disc=compe,
        team_tag_disc=team,
        user_tag_disc=user,
        comment_field_disc=comment,
        # author_user_nickname=user.nickname,
        # author_user_id=user.id,
        # author_team_name=user.selectedTeam.name,
        # author_team_id=user.selectedTeam.id,
    )


class DiscussionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # テスト用ユーザ
        cls.user = User.objects.create_user(
                username='testuser1', password='secret1',
                )

        # テスト用チームタグ
        cls.teamtag1 = TeamTag(name='testtag1')
        cls.teamtag2 = TeamTag(name='testtag2')
        cls.teamtag1.save()
        cls.teamtag2.save()

        # テスト用コンペティション
        cls.compes = launch_competition()

        cls.thread = _create_thread(
            cls.user, cls.compes[0], cls.teamtag1,
            title='test issue',
            comment='This is an example of discussion thread.')
        cls.thread.save()

    def test_thread_user_team_name_id_filled(self):
        """議題に投稿者情報が転写されているか."""
        self.assertEqual(self.thread.author_team_id, self.teamtag1.id)
        self.assertEqual(self.thread.author_user_id, self.user.id)
        self.assertEqual(self.thread.author_team_name, self.teamtag1.name)
        self.assertEqual(self.thread.author_user_nickname, self.user.nickname)


class DiscussionPostTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # テスト用ユーザ
        cls.user = User.objects.create_user(
                username='testuser1', password='secret1',
                )

        # テスト用チームタグ
        cls.teamtag1 = TeamTag(name='testtag1')
        cls.teamtag2 = TeamTag(name='testtag2')
        cls.teamtag1.save()
        cls.teamtag2.save()

        # テスト用コンペティション
        cls.compes = launch_competition()

        cls.thread = _create_thread(
            cls.user, cls.compes[0], cls.teamtag1,
            title='test issue',
            comment='This is an example of discussion thread.')
        cls.thread.save()

        cls.thread_comment = DiscussionPost(
            post_tag_post=cls.thread,
            team_tag_post=cls.teamtag1,
            user_tag_post=cls.user,
            comment_field_post='test comment',
            )
        cls.thread_comment.save()

    def test_thread_comment_user_team_name_id_filled(self):
        """議題投稿に投稿者情報が転写されているか."""
        self.assertEqual(self.thread_comment.author_team_id, self.teamtag1.id)
        self.assertEqual(self.thread_comment.author_user_id, self.user.id)
        self.assertEqual(self.thread_comment.author_team_name, self.teamtag1.name)
        self.assertEqual(self.thread_comment.author_user_nickname, self.user.nickname)
