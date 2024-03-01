from django.shortcuts import render
from django.urls import reverse_lazy
from django.http import Http404
from django.http import HttpResponseRedirect
from django.utils import timezone, dateformat
from django.views.generic import (ListView, UpdateView)
from django.contrib.auth.mixins import LoginRequiredMixin  # 追加
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.utils.dateparse import parse_datetime
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from competitions.models import CompetitionModel
from .forms import login_requiredForm

from accounts.models import TeamTag
from universityofbigdata.utils import (
        get_ip_address, get_user_info, get_log_reader,
        )
from management.models import ConfigBox
import logging

logger = logging.getLogger(__name__)

def prepare_top_context(request):
    """トップ画面に必要なコンテキストを作成."""
    # ユーザー名
    user_name, user_id, team_name, team_id = get_user_info(request)
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
    # NOTE: コンペの状態変化の最新10件を表示している
    log_data = [data for data in get_log_reader()]

    num_competition_logs = 5
    manage_box = []
    for log_entry in reversed(log_data):
        if len(manage_box) >= num_competition_logs:
            break
        if 'competition_id' in log_entry.keys():
            manage_box.append({
                'time': log_entry['time'],
                'message': log_entry['message'],
                })

    # 閲覧者ログ
    num_activity_logs = 5
    activity_logs = []
    last_msg = None
    for log_entry in reversed(log_data):
        if len(activity_logs) >= num_activity_logs:
            break
        if ('user_name' in log_entry.keys()) and (
                user_name == log_entry['user_name']):
            activity_msg = f"{log_entry['message']} from {log_entry['ip']}"
            if (last_msg is None) or (last_msg != activity_msg):
                activity_logs.append({
                    'time': parse_datetime(log_entry['time']),
                    'activity': activity_msg})
                last_msg = activity_msg

    # インスタンス上のアクティビティ
    num_other_user_logs = 5
    other_user_logs = []
    last_msg = None
    for log_entry in reversed(log_data):
        if len(other_user_logs) >= num_other_user_logs:
            break
        if log_entry.get('user_id') \
                and (log_entry.get('user_id') > 0) \
                and ('action' in log_entry.keys()) \
                and (log_entry['action'].get('name') != 'access_page'):
            msg = f"""{log_entry['user_name']} {_('の活動: ')} """ \
                  f"""{log_entry['message']}"""
            if (last_msg is None) or (last_msg != msg):
                other_user_logs.append({
                    'time': parse_datetime(log_entry['time']),
                    'activity': msg})
                last_msg = msg

    # コンペティション情報
    competition_part = CompetitionModel.objects.filter(status='active')
    Current_Competitions_box = []
    for comp in competition_part:
        if(comp.public):
            mass_public = _('公開')
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
            mass_public = _('公開')
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
            'other_user_logs': other_user_logs,
            'manage_box': manage_box,
            }


def top(request):
    """トップ画面の表示."""
    return render(request, 'top.html', prepare_top_context(request))


def not_implemented(request):
    """「実装されていません」のページを表示."""
    return render(request, 'not_implemented.html')


@login_required
def login_required(request):
    """ログイン画面の表示.
    """
    # 参加招待コード取得
    authentication_code = ConfigBox.objects.get(id=1).authentication_code

    # Post確認
    if request.method == "POST":
        form = login_requiredForm(request.POST)
        id_code = request.POST.get('invitation_code')
        if(authentication_code == id_code):
            request.user.is_participant=True
            request.user.save()
            logger.info(
                _('参加認証に成功しました'),
                extra={
                  'request': request,
                  'action': {
                    'name': 'authentication',
                    'is_valid': True,
                  }
                })
        else:
            logger.info(
                _('参加認証に失敗しました'),
                extra={
                  'request': request,
                  'action': {
                    'name': 'authentication',
                    'is_valid': False,
                  }
                })
    else:
        form = login_requiredForm()
    
    return render(
            request, 'login_required.html',
            {'form': form})


# google認証
def LoginView(request):
    """Google OAuth2 による認証ページ."""
    # logging
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
