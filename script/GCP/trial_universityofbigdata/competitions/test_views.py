from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from parametrize import parametrize

import numpy as np
from lxml import etree

from competitions.models import (
        METRICS, CompetitionModel, CompetitionPost
        )
from accounts.models import TeamTag

# Userモデル `accounts.User` を取得
User = get_user_model()


def _create_test_user():
    return User.objects.create_user(
            username='testuser1', password='secret1',
            )


def launch_competition():
    compes = []
    for i, (m_name, m_desc) in enumerate(METRICS):
        # 提出例ファイル
        pred_file = SimpleUploadedFile(
            "example_pred.csv",
            b"image,label\ntest_0001.png,0"
        )
        # 正解ファイル
        gt_file = SimpleUploadedFile(
            "gt.csv",
            b"image,label\ntest_0001.png,0"
        )

        compes.append(CompetitionModel.objects.create(
            title='画像分類', title_en='Image Classification',
            competition_abstract='画像の分類精度を競います。',
            competition_description='画像を分類し、画像分類の評価指標により自動で評価を行います。',
            problem_type='classification',
            evaluation_type=m_name,
            file_description='画像の正解ラベル',
            blob_key=pred_file,
            truth_blob_key=gt_file,
            open_datetime=timezone.make_aware(timezone.datetime(
                2023, 7, 11, 9, 0)),
            close_datetime=timezone.make_aware(timezone.datetime(
                2023, 7, 31, 18, 0)),
            status='active',
            )
        )
    return compes


def prepare_files(
        pred=[0, 1, 1], gt=[0, 1, 2]
        ):
    # 提出ファイル例?
    desc_file = SimpleUploadedFile(
        "desc.csv",
        "\n".join([
            f'{v}' for i, v in enumerate(pred)
            ]).encode()
    )
    # 正解ファイル
    gt_file = SimpleUploadedFile(
        "gt.csv",
        "\n".join([
            f'{v}' for i, v in enumerate(gt)
            ]).encode()
    )

    # 提出ファイル
    submission_file = SimpleUploadedFile(
        "pred.csv",
        "\n".join([
            f'{v}' for i, v in enumerate(pred)
            ]).encode()
    )
    return desc_file, gt_file, submission_file


class CompetitionViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # テスト用コンペティション登録
        launch_competition()

        # テスト用チームタグ
        cls.teamtag1 = TeamTag(name='testtag1')
        cls.teamtag2 = TeamTag(name='testtag2')
        cls.teamtag1.save()
        cls.teamtag2.save()

        # テスト用ユーザ登録
        cls.test_user1 = User.objects.create(
                username='testuser1', password='password1',
                selectedTeam=cls.teamtag1,
                )
        cls.test_user1.team_tags.add(cls.teamtag1)
        cls.test_user1.team_tags.add(cls.teamtag2)
        cls.test_user1.save()

        # テスト用提出ファイル
        cls.submission_file = SimpleUploadedFile(
            "submission.csv",
            b"image,label\ntest_0001.png,0"
        )


    @parametrize(
            'name, args, status_code',
            [
                #('competitions_create', None, 404),
                ('competitions_list', None, 404),
                ('competitions_main', [1], 404),
                ('competitions_data', [1], 404),
                ('competitions_post', [1], 404),
                ('competitions_ranking', [1], 404),
            ])
    def test_expected_status_code_when_not_logged_in(self, name, args, status_code):
        response = self.client.get('Competitions:' + name, args=args)
        self.assertEqual(response.status_code, status_code)

    @parametrize(
            'name, args',
            [
                #('competitions_create', None),
                ('competitions_list', None),
                ('competitions_main', [1]),
                ('competitions_data', [1]),
                ('competitions_post', [1]),
                ('competitions_ranking', [1]),
            ])
    def test_view_membership_url(self, name, args):
        self.client.force_login(self.test_user1)
        response = self.client.get(reverse('Competitions:'+name, args=args))
        self.assertEqual(response.status_code, 200)

    @parametrize(
            'm_name, pred, gt, expected_score',
            [
                ('mean_absolute_error', np.arange(10), np.arange(10), 0),
                ('mean_squared_error', np.arange(10), np.arange(10), 0),
                ('roc_auc_score', [0, 1, 1, 0, 0], [0, 1, 1, 0, 0], 1),
                ('accuracy', np.arange(10), np.arange(10), 1),
                ('recall', np.arange(10), np.arange(10), 1),
                ('precision', np.arange(10), np.arange(10), 1),
                ('f1', np.arange(10), np.arange(10), 1),
                ('root_mean_squared_error', np.arange(10), np.arange(10), 0),
                ('mean_roc_auc_score', [0, 1, 1, 0, 0], [0, 1, 1, 0, 0], 1),
            ])
    def test_view_submission(self, m_name, pred, gt, expected_score):
        """評価指標ごとに入出力をテストします."""
        desc_file, gt_file, submission_file = prepare_files(pred, gt)

        # コンペティション作成
        comp = CompetitionModel.objects.create(
            title=f'{m_name}を使ったコンペのテスト',
            title_en=f'A test competition evaluating with {m_name}',
            competition_abstract=f'{m_name}で評価するコンペのテストです。',
            competition_description='{m_name}で評価するコンペのテストです。',
            problem_type='classification',
            evaluation_type=m_name,
            file_description='ファイルの説明欄',
            blob_key=desc_file,
            truth_blob_key=gt_file,
            open_datetime=timezone.make_aware(timezone.datetime(
                2023, 7, 11, 9, 0)),
            close_datetime=timezone.make_aware(timezone.datetime(
                2023, 7, 31, 18, 0)),
            status='active',
            )

        # ログイン
        self.client.force_login(self.test_user1)

        # 投稿
        res_post = self.client.post(
            f'/ja/competitions/competitions_post/{comp.id}',
            {
                'post_key': submission_file,
                'count_par_today': 0,  # FIXME: 当日の投稿数が任意に指定できるバグ
            })

        # リーダーボード取得
        res_get = self.client.get(
                reverse('Competitions:competitions_ranking', args=[comp.id]))
        td = etree.HTML(res_get.content.decode()).cssselect('table')[1][0]

        self.assertEqual(td[1][0].text, '1 / 1')  # submitted once
        # team name
        self.assertEqual(td[1][1].text, self.test_user1.selectedTeam.name)
        self.assertEqual(td[1][2].text, self.test_user1.nickname)
        self.assertEqual(td[1][3].text, f'{expected_score:.3f}')  # score
        # self.assertEqual(td[1][3].text, '')  # submission date

    def _test_wrong_formatted_submisson(
            self, m_name='accuracy',
            pred=np.arange(10), gt=np.arange(10), expected_score=1):
        """投稿ファイルのフォーマットに問題がある場合に例外処理できているか."""
        desc_file, gt_file, _ = prepare_files(pred, gt)

        submission_file = SimpleUploadedFile(
            "wrong_pred.csv",
            '\n'.join(['aaa' for _ in range(len(gt))]).encode()
        )

        # コンペティション作成
        comp = CompetitionModel.objects.create(
            title=f'{m_name}を使ったコンペのテスト',
            title_en=f'A test competition evaluating with {m_name}',
            competition_abstract=f'{m_name}で評価するコンペのテストです。',
            competition_description='{m_name}で評価するコンペのテストです。',
            problem_type='classification',
            evaluation_type=m_name,
            file_description='ファイルの説明欄',
            blob_key=desc_file,
            truth_blob_key=gt_file,
            open_datetime=timezone.make_aware(timezone.datetime(
                2023, 7, 11, 9, 0)),
            close_datetime=timezone.make_aware(timezone.datetime(
                2023, 7, 31, 18, 0)),
            status='active',
            )

        # ログイン
        self.client.force_login(self.test_user1)

        # 投稿
        res_post = self.client.post(
            f'/ja/competitions/competitions_post/{comp.id}',
            {
                'post_key': submission_file,
                'count_par_today': 0,
            })
        self.assertEqual(res_post.status_code, 200)

    def test_submission_counts_on_the_day(
            self, m_name='accuracy',
            pred=np.arange(10), gt=np.arange(10), expected_score=1):
        """当日中の投稿回数が正しいか."""
        desc_file, gt_file, submission_file = prepare_files(pred, gt)

        # コンペティション作成
        comp = CompetitionModel.objects.create(
            title=f'{m_name}を使ったコンペのテスト',
            title_en=f'A test competition evaluating with {m_name}',
            competition_abstract=f'{m_name}で評価するコンペのテストです。',
            competition_description='{m_name}で評価するコンペのテストです。',
            problem_type='classification',
            evaluation_type=m_name,
            file_description='ファイルの説明欄',
            blob_key=desc_file,
            truth_blob_key=gt_file,
            open_datetime=timezone.make_aware(timezone.datetime(
                2023, 7, 11, 9, 0)),
            close_datetime=timezone.make_aware(timezone.datetime(
                2023, 7, 31, 18, 0)),
            status='active',
            )

        # ログイン
        self.client.force_login(self.test_user1)

        # 投稿
        n_submission = 5
        n_max_submissions_per_day = 3
        for i in range(n_submission):
            desc_file, gt_file, submission_file = prepare_files(pred, gt)
            res_post = self.client.post(
                reverse('Competitions:competitions_post', args=[comp.id]),
                {
                    'post_key': submission_file,
                    'count_par_today': 0,  # 当日の投稿数が任意に指定できるバグが無いことをついでに確認
                }
            )

        # リーダーボード取得
        res_get = self.client.get(
                reverse('Competitions:competitions_ranking', args=[comp.id]))
        td = etree.HTML(res_get.content.decode()).cssselect('table')[1][0]

        for i in range(1, n_max_submissions_per_day):
            self.assertEqual(td[i][0].text[0], f'{i}')
