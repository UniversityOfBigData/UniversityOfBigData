from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from parametrize import parametrize

import numpy as np
from lxml import etree
from scipy.stats import rankdata

from static.lib import metrics
from competitions.models import (
        CompetitionModel, CompetitionPost
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
    for i, m_name in enumerate(metrics.keys()):
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
        gt=[0, 1, 2],
        pred=[0, 1, 1],
        ):
    # 訓練・予測用データ
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

        # テスト用ユーザとチームタグの登録
        cls.users = []
        cls.teamtags = []
        cls.num_test_users = 5
        for i in range(cls.num_test_users):
            teamtag = TeamTag(name=f'testtag{i}')
            teamtag.save()
            test_user = User.objects.create(
                    username=f'testuser{i}',
                    password=f'password{i}',
                    email=f'testuser{i}@example.ac.jp',
                    selectedTeam=teamtag,
                    )
            test_user.save()
            cls.users.append(test_user)
            cls.teamtags.append(teamtag)

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
        self.client.force_login(self.users[0])
        response = self.client.get(reverse('Competitions:'+name, args=args))
        self.assertEqual(response.status_code, 200)

    def _test_view_submission(self, m_name, gt, preds, expected_scores):
        desc_file, gt_file, _ = prepare_files(gt, preds[0])

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
            public_leaderboard_percentage=100,
            status='active',
            )

        expected_ranks = rankdata(
                -(2*metrics[m_name].greater_is_better - 1)*np.array(
                    expected_scores),
                method='min')

        for i in range(preds.shape[0]):
            # ログイン
            self.client.force_login(self.users[i])

            _, _, submission_file = prepare_files(gt, preds[i])

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
            self.assertEqual(td[1][1].text, self.users[i].selectedTeam.name)
            self.assertEqual(td[1][2].text, self.users[i].nickname)
            # NOTE: デフォルトでは小数点以下5桁まで表示する
            self.assertEqual(td[1][3].text, f'{expected_scores[i]:.5f}')  # score
            # self.assertEqual(td[1][3].text, '')  # submission date

        # 順位が正しいか確認する
        for i in range(preds.shape[0]):
            user_name = etree.HTML(res_get.content.decode()).cssselect(
                    'table')[0][0][i+1][1].text.split('/')[1].strip()
            actual_rank = int(etree.HTML(res_get.content.decode()).cssselect(
                    'table')[0][0][i+1][0].text)
            for j in range(len(self.users)):
                if user_name == self.users[j].username:
                    assert actual_rank == expected_ranks[j]

    # np.round(10*(2*np.random.rand(10)-1), 3) で乱数生成
    FLOAT_GT = np.array([
        0.298,  8.439, -6.638, -4.886,  9.884, -5.206,  4.594,  6.167,
        5.469,  3.097
        ])
    FLOAT_PREDS = np.array([[
        -6.439, -4.516, -6.996,  7.625, -9.335,  0.382,  0.637,  8.738,
        -4.945,  6.294
        ], [
        -8.117, -6.561,  5.734,  4.266,  0.423, -7.415, -1.12,  9.493,
        -5.174, -5.373
        ], [
        -6.309, -7.228, -8.525,  8.419,  9.736,  9.171,  5.443, -4.832,
        2.418,  8.284
        ]])
    # np.random.randint(10, size=10) で乱数生成
    INT_GT = np.array([3, 2, 8, 7, 5, 6, 9, 9, 2, 6])
    INT_PREDS = np.array([[
        7, 5, 0, 4, 8, 1, 8, 4, 8, 6
        ], [
        0, 2, 2, 2, 0, 8, 5, 6, 9, 6
        ], [
        6, 4, 9, 4, 7, 7, 9, 7, 5, 4
        ]])

    @parametrize(
            'm_name, gt, preds, expected_scores',
            [(
                'mean_absolute_error',
                FLOAT_GT, FLOAT_PREDS,
                [7.7507, 8.4762, 7.2077],
             ),
             (
                'mean_squared_error',
                FLOAT_GT, FLOAT_PREDS,
                [91.14082790000002, 85.57543360000003, 83.4323537]
             ),
             (
                'root_mean_squared_error',
                FLOAT_GT, FLOAT_PREDS,
                [9.546770548201104, 9.250699087096068, 9.134131250425515]
             ),
             (
                'roc_auc_score',
                (FLOAT_GT > 0).astype(int),
                FLOAT_PREDS,
                [0.4761904761904762, 0.380952380952381, 0.4285714285714286]
             ),
             (
                 'accuracy',
                 INT_GT, INT_PREDS,
                 [0.1, 0.2, 0.1]
             ),
             (
                 'recall',
                 np.mod(INT_GT, 2), np.mod(INT_PREDS, 2),
                 [0.4, 0.5, 0.5]
             ),
             (
                 'precision',
                 np.mod(INT_GT, 2), np.mod(INT_PREDS, 2),
                 [0.38095238095238093, 0.5, 0.5]
             ),
             (
                 'f1',
                 np.mod(INT_GT, 2), np.mod(INT_PREDS, 2),
                 [0.375, 0.4505494505494506, 0.4949494949494949]
             ),
             # 複数列 (多次元) のケース
             # 多次元回帰
             (
                 'mean_absolute_error',
                 np.array(['0, 1, 2, 3', '4, 5, 6, 7']),
                 np.array([['0, 1, 2, 3', '4, 5, 6, 7']]),
                 [0]),
             (
                 'mean_absolute_error',
                 np.array(['0, 1, 2, 3', '4, 5, 6, 7']),
                 np.array([['1, 1, 2, 3', '4, 5, 6, 7']]),
                 [0.125]),  # (絶対誤差 / カラム数) / サンプルサイズ
             (
                 'root_mean_squared_error',
                 np.array(['0, 1, 2, 3', '4, 5, 6, 7']),
                 np.array([['0, 1, 2, 3', '4, 5, 6, 7']]),
                 [0]),
             # 多ラベル分類
             (
                 'exact_match_ratio',
                 np.array(['0, 1, 2, 3', '4, 5, 6, 7']),
                 np.array([['1, 1, 2, 3', '4, 5, 6, 7']]),
                 [0.5]),
             # カスタム指標
             #('my_metric',
             #    ['1, 1, 2, 3', '4, 5, 6, 7'],
             #    ['1, 0, 0, 0', '0, 0, 0, 0'],
             #    1),
            ])
    def test_view_submission(self, m_name, gt, preds, expected_scores):
        """評価指標ごとに入出力をテストします (パブリックリーダーボードのみ)."""
        self._test_view_submission(m_name, gt, preds, expected_scores)

    def test_view_custom_metrics(self):
        """カスタム指標の動作テスト."""
        import importlib
        if importlib.util.find_spec('static.lib.user_defined'):
            self._test_view_submission(
                    'my_metric', ['1, 1, 2, 3', '4, 5, 6, 7'],
                    ['1, 0, 0, 0', '0, 0, 0, 0'],
                    1)

    def _test_wrong_formatted_submisson(
            self, m_name='accuracy',
            pred=np.arange(10), gt=np.arange(10), expected_score=1):
        """投稿ファイルのフォーマットに問題がある場合に例外処理できているか."""
        desc_file, gt_file, _ = prepare_files(gt, pred)

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
        self.client.force_login(self.users[0])

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
        desc_file, gt_file, submission_file = prepare_files(gt, pred)

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
        self.client.force_login(self.users[0])

        # 投稿
        n_submission = 5
        n_max_submissions_per_day = 3
        for i in range(n_submission):
            desc_file, gt_file, submission_file = prepare_files(gt, pred)
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
