from django.shortcuts import render
from django.urls import reverse_lazy
from django.http import Http404
from django.http import HttpResponseRedirect
from django.utils import timezone, dateformat
from django.views.generic import (ListView, UpdateView)
from django.contrib.auth.mixins import LoginRequiredMixin  # 追加
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from competitions.models import CompetitionModel
from .forms import login_requiredForm

from accounts.models import TeamTag
from universityofbigdata.lib.mylogger import (
        get_ip_address, get_user_name,
        # get_now_time, get_log_box, set_log_box
        )
from management.models import ConfigBox
from universityofbigdata.lib.mylogger import set_log_box_lite
from userlog.models import get_mlog_box
import logging
import ast

logger = logging.getLogger(__name__)


def set_team(request):
    # チームのセット (1人1チームの時の設定)
    team_set = TeamTag.objects.all()
    team_count = len(team_set) + 1
    initial_team_name = 'InitialTeam'+str(team_count)

    def check_is_team(initial_team_name):
        q = TeamTag.objects.filter(name=initial_team_name)
        return (q.first() is None)

    if not (check_is_team(initial_team_name)):
        addstr = ''
        while True:
            addstr = addstr + 'X'
            initial_team_name = 'InitialTeam'+addstr+str(team_count)
            if check_is_team(initial_team_name):
                break
    print(initial_team_name)
    part_obj = TeamTag.objects.create(name=initial_team_name)
    request.user.team_tags.add(part_obj)
    request.user.selectedTeam = part_obj
    return request


def prepare_top_context(request):
    """トップ画面に必要なコンテキストを作成."""
    # ユーザー名
    username = get_user_name(request)
    # アクセス者のIPアドレス取得
    client_ip, client_WAN_ip = get_ip_address(request)
    # ユーザー数
    users_num = get_user_model().objects.all().count()
    # コンペティション数
    pub_competition_num = CompetitionModel.objects.all().filter(
            public=True).count()
    closed_competition_num = CompetitionModel.objects.all().filter(
            public=False).count()
    # 時刻
    # now_time = get_now_time()
    # 記事
    # 管理ログ
    manage_log_objs = get_mlog_box()
    manage_logs = manage_log_objs.log_field
    manage_logs = manage_logs.replace('\r', '')
    manage_log_list = manage_logs.split(', \n')
    manage_box = []
    for m_str in manage_log_list:
        m_dict = ast.literal_eval(m_str)
        manage_box.append(m_dict)
    # 後ろから10個
    N = 10
    manage_box = manage_box[-N:]
    # 閲覧者ログ
    activity_logs = []
    mess = {}
    mess['time'] = dateformat.format(
            timezone.localtime(timezone.now()), 'Y-m-d H:i')
    m = str(username) + ' , your_ip : ' + str(client_ip) \
        + ' Welcome to test site.' + ' This site under operation check.'
    mess['log'] = m
    activity_logs.append(mess)
    # コンペティション情報
    competition_part = CompetitionModel.objects.filter(status='active')
    Current_Competitions_box = []
    for comp in competition_part:
        if(comp.public):
            mass_public = _('公　開')
        else:
            mass_public = _('非公開')
        if(comp.invitation_only):
            mess_inv_only = _('参加者制限あり')
        else:
            mess_inv_only = _('参加者制限なし')
        if(comp.public):
            a = [str(comp.title), str(comp.competition_abstract),
                 mass_public+' / '+mess_inv_only]
        else:
            a = [str(comp.title), mass_public+' / '+mess_inv_only]
        b = [dateformat.format(
                timezone.localtime(comp.open_datetime),
                '開始：Y-m-d H:i'),
             dateformat.format(
                 timezone.localtime(comp.close_datetime),
                 '終了：Y-m-d H:i')]
        box = [a, b]
        Current_Competitions_box.append(box)
    is_NoCurrentCompetitions = (len(Current_Competitions_box) == 0)
    # 開催準備コンペティション
    competition_part = CompetitionModel.objects.filter(status='coming')
    Coming_Competitions_box = []
    for comp in competition_part:
        if(comp.public):
            mass_public = _('公　開')
        else:
            mass_public = _('非公開')
        if(comp.invitation_only):
            mess_inv_only = _('参加者制限あり')
        else:
            mess_inv_only = _('参加者制限なし')
        if(comp.public):
            a = [str(comp.title), str(comp.competition_abstract),
                 mass_public + ' / ' + mess_inv_only]
        else:
            a = [str(comp.title), mass_public + ' / ' + mess_inv_only]
        b = [
                dateformat.format(
                    timezone.localtime(comp.open_datetime), '開始：Y-m-d H:i'),
                dateformat.format(
                    timezone.localtime(comp.close_datetime), '終了：Y-m-d H:i')
                ]
        box = [a, b]
        Coming_Competitions_box.append(box)
    is_NoComingCompetitions = (len(Coming_Competitions_box) == 0)
    # logging
    message = set_log_box_lite('show top page', request)
    logger.info(message)

    return {
            'client_ip': client_ip,
            'client_WAN_ip': client_WAN_ip,
            'users_num': users_num,
            'CurrentCompetitions': is_NoCurrentCompetitions,
            'CurrentCompetitions_box': Current_Competitions_box,
            'ComingCompetitions': is_NoComingCompetitions,
            'ComingCompetitions_box': Coming_Competitions_box,
            'publicCompetition_num': pub_competition_num,
            'closedCompetition_num': closed_competition_num,
            'activity_logs': activity_logs,
            'manage_box': manage_box,
            }


def top(request):
    """トップ画面の表示."""
    return render(request, 'top.html', prepare_top_context(request))


def not_implemented(request):
    """「実装されていません」のページを表示."""
    return render(request, 'not_implemented.html')


def prepare_login_required_context(request):
    # logging
    message = set_log_box_lite('login successful', request)
    logger.info(message)
    # コード取得
    sin_in_config = ConfigBox.objects.get(name='signInCode')

    # FIXME: setup_temp.pyを実行していれば、sin_in_config is None にはならない
    #        ConfigBoxが1つもない場合、上記getでDoesNotExistエラーが返される
    if(sin_in_config is None):
        authentication_code = "XYZxyz095"  # issue #25
        auto_team_setter = True
    else:
        authentication_code = sin_in_config.authentication_code
        auto_team_setter = sin_in_config.auto_team_set_flag

    # Post確認
    if request.method == "POST":
        form = login_requiredForm(request.POST)
        id_code = request.POST.get('invitation_code')
        if(authentication_code == id_code):
            # チーム自動割付機能
            if(auto_team_setter):
                # チーム未割付時には付与する
                if(request.user.selectedTeam is None):
                    # 割付
                    request = set_team(request)
            request.user.is_participant = True
            request.user.save()
            # logging
            message = set_log_box_lite('passed invitation', request)
            logger.info(message)
    else:
        form = login_requiredForm()
    return {'form': form}


@login_required
def login_required(request):
    """ログイン画面の表示.

    NOTE: 使われていない.
    """

    return render(
            request, 'login_required.html',
            prepare_login_required_context(request))


# google認証
def LoginView(request):
    """Google OAuth2 による認証ページ."""
    # logging
    message_part = 'try google login'
    message = set_log_box_lite(message_part, request)
    logger.info(message)
    return HttpResponseRedirect(
            'social:begin', kwargs=dict(backend='google-oauth2'))


def participation_guide(request):
    """「参加案内」ページ."""
    # 参加者案内
    # issue #26
    params = {  # <- 渡したい変数を辞書型オブジェクトに格納
        'max_submissions_per_day': 3,
    }
    return render(request, 'participation_guide.html', params)




