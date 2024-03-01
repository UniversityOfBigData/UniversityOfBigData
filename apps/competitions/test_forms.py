"""Test forms."""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.translation import gettext_lazy as _

from .forms import (
    CompetitionPostCreateForm,
    )

User = get_user_model()


class CompetitionPostCreateFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='test_user', email='test@test',
        )

    def test_ValidationError_filename_not_endswith_csv(self):
        """clean_post_keyで拡張子が.csvでない場合にエラーを出すか."""
        submission_file = SimpleUploadedFile(
            "pred.txt",
            "\n".join([
                f'{v}' for i, v in enumerate([0, 1, 1])
                ]).encode()
        )
        data = {'count_par_today': 0}
        file_data = {'post_key': submission_file}
        form = CompetitionPostCreateForm(data, file_data, instance=self.user)

        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error('post_key'))
        self.assertEqual(form.errors['post_key'], [_('拡張子はcsvのみです')])

    def test_filename_endswith_csv(self):
        """clean_post_keyで拡張子が.csvになっている場合にvalidか."""
        submission_file = SimpleUploadedFile(
            "pred.csv",
            "\n".join([
                f'{v}' for i, v in enumerate([0, 1, 1])
                ]).encode()
        )
        data = {'count_par_today': 0}
        file_data = {'post_key': submission_file}
        form = CompetitionPostCreateForm(data, file_data, instance=self.user)

        self.assertTrue(form.is_valid())
        self.assertFalse(form.has_error('post_key'))
