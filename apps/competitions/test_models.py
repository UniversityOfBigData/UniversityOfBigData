"""Test models."""

from django.test import TestCase, TransactionTestCase
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from time import sleep

import numpy as np

from competitions.models import (
        CompetitionModel, CompetitionPost,
        )
from competitions.management.commands.runapscheduler import setplan01


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


def launch_competition():
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

    CompetitionModel.objects.create(
        title='画像分類', title_en='Image Classification',
        competition_abstract='画像の分類精度を競います。',
        competition_description='画像を分類し、画像分類の評価指標により自動で評価を行います。',
        problem_type='classification',
        evaluation_type='accuracy',
        file_description='画像の正解ラベル',
        blob_key=pred_file,
        truth_blob_key=gt_file,
        open_datetime=timezone.make_aware(timezone.datetime(
            2023, 7, 11, 9, 0)),
        close_datetime=timezone.make_aware(timezone.datetime(
            2023, 7, 31, 18, 0)),
        status='active',
        )


class CompetitionModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        launch_competition()

    def test_title_label(self):
        """コンペのタイトルのフィールド名が想定通りか."""
        compe = CompetitionModel.objects.get(id=1)
        field_label = compe._meta.get_field('title').verbose_name
        self.assertEqual(field_label, 'コンペティションのタイトル（日本語）')

    def test_owner_name_lost_if_None(self):
        """owner_nameが未設定の場合、owner lostが代入されているか."""
        compe = CompetitionModel.objects.get(id=1)
        self.assertEqual(compe.owner_name, 'owner lost')


class CompetitionPostTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        launch_competition()
        compe = CompetitionModel.objects.get(id=1)
        submission_file = SimpleUploadedFile(
            "submission.csv",
            b"image,label\ntest_0001.png,0"
        )
        CompetitionPost.objects.create(
            post=compe,
            post_key=submission_file
        )

    def test_count_posts_equals_1(self):
        """投稿数が1になっているか."""
        compe_post = CompetitionPost.objects.get(id=1)
        self.assertEqual(compe_post.count_posts, 1)
        self.assertEqual(compe_post.count_par_today, 1)

    def test_wrong_csv_posted(self):
        """XXX: 作成途中、不正なCSVデータが投稿された場合に例外処理されるか."""
        compe = CompetitionModel.objects.get(id=1)
        submission_file = SimpleUploadedFile(
            "submission.csv",
            b"image"
        )
        CompetitionPost.objects.create(
            post=compe,
            post_key=submission_file
        )


class StatusUpdateTests(TransactionTestCase):
    def test_comp_status_update(self):
        """コンペの状態更新がうまくできているか."""
        pred = np.arange(10)
        gt = np.arange(10)
        desc_file, gt_file, submission_file = prepare_files(pred, gt)

        # コンペティション作成
        title = 'コンペの状態更新のテスト'
        comp = CompetitionModel.objects.create(
            title=title,
            title_en='A test of the scheduler',
            competition_abstract='スケジューラのテストです。',
            competition_description='スケジューラのテストです。',
            problem_type='classification',
            evaluation_type='accuracy',
            file_description='ファイルの説明欄',
            blob_key=desc_file,
            truth_blob_key=gt_file,
            open_datetime=timezone.now() + timezone.timedelta(seconds=3),
            close_datetime=timezone.now() + timezone.timedelta(seconds=6),
            status='coming',
            )
        setplan01()

        self.assertEqual(comp.status, 'coming')

        sleep(4)
        setplan01()

        comp = CompetitionModel.objects.get(title=title)
        self.assertEqual(comp.status, 'active')

        sleep(4)
        setplan01()

        comp = CompetitionModel.objects.get(title=title)
        self.assertEqual(comp.status, 'completed')
