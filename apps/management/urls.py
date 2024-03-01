from django.urls import path
from django.utils.translation import gettext_lazy as _

from universityofbigdata.utils import access_recorded
from management import views
from management.views import logger


urlpatterns = [
    path('competitions_create/', access_recorded(
        logger, 'create_competition', _('コンペティション作成ページ'))(
            views.CompetitionsCreateView.as_view()),
        name='competitions_create'),
    path('certification_teams/', access_recorded(
        logger, 'private_competition', _('非公開コンペティション設定ページ'))(
            views.CertificationTeamsView.as_view()),
        name='certification_teams'),
    path('make_team/', access_recorded(
        logger, 'create_team', _('チーム作成ページ'))(
            views.MakeTeamsView.as_view()), name='make_team'),
    path('manage_teams/', access_recorded(
        logger, 'team_management', _('チーム管理ページ'))(
            views.ManageTeamsView.as_view()), name='manage_teams'),
    path('suspension_users/', access_recorded(
        logger, 'user_management', _('ユーザー管理ページ'))(
            views.SuspensionUsersView.as_view()), name='suspension_users'),
    path('registration_users/', access_recorded(
        logger, 'user_registration', _('ユーザー登録ページ'))(
            views.RegistrationUsersView.as_view()), name='registration_users'),
    path('edit_config/<int:pk>', access_recorded(
        logger, 'configuration', _('参加認証コード設定ページ'))(
        views.EditConfigBoxView.as_view()), name='edit_config'),
]
