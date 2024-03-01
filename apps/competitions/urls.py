from django.urls import path
from django.utils.translation import gettext_lazy as _

from universityofbigdata.utils import access_recorded
from competitions import views
from competitions.views import logger


app_name = "Competitions"

urlpatterns = [
    path('competitions_list/', access_recorded(
        logger, 'competitions_list', _('コンペティション一覧ページ'))(
        views.CompetitionsListView.as_view()), name='competitions_list'),
    path('competitions_main/<int:pk>', access_recorded(
        logger, 'competitions_main', _('コンペティションのメインページ'))(
        views.CompetitionsMainView.as_view()), name='competitions_main'),
    path('competitions_data/<int:pk>', access_recorded(
        logger, 'competitions_data', _('コンペティションのデータページ'))(
        views.CompetitionsDataView.as_view()), name='competitions_data'),
    path('competitions_post/<int:pk>', access_recorded(
        logger, 'competitions_post', _('コンペティションのデータ投稿ページ'))(
        views.CompetitionsPostView.as_view()), name='competitions_post'),
    path('competitions_ranking/<int:pk>', access_recorded(
        logger, 'competitions_ranking', _('コンペティションのリーダーボード'))(
        views.CompetitionsRankingView.as_view()), name='competitions_ranking'),
]
