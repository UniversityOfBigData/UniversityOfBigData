import logging

from django.http import Http404
from django.db.models import Q
from django.shortcuts import render
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied
from django.views.generic import ListView, UpdateView
from django.views.generic.edit import CreateView, FormMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from .forms import CompetitionForm, CertificationTeamsForm, MakeTeamForm, ManageUsersForm, EditConfigBoxForm
from .models import ConfigBox

from accounts.models import User, TeamTag
from competitions.models import CompetitionModel

logger = logging.getLogger(__name__)

# Create your views here.


class CompetitionsCreateView(LoginRequiredMixin, CreateView):
    model = CompetitionModel
    form_class = CompetitionForm
    template_name = 'competitions_create.html'
    success_url = '/'

    def form_invalid(self, form):
        logger.error(
                _('コンペティション作成に失敗しました: ') + '\n' + form.errors.as_text(),
                extra={
                    'request': self.request,
                    'action': {
                        'name': 'launch_competition',
                        'is_valid': False,
                        }
                    }
                )
        return super().form_invalid(form)

    def form_valid(self, form):
        logger.info(
                _('コンペティションを作成しました'),
                extra={
                    'request': self.request,
                    'action': {
                        'name': 'launch_competition',
                        'is_valid': True,
                        }
                    }
                )
        return super().form_valid(form)


class CertificationTeamsView(LoginRequiredMixin, FormMixin, ListView):
    #テーブル連携
    model = TeamTag
    #レコード情報をテンプレートに渡すオブジェクト
    context_object_name = "team_box"
    #テンプレートファイル連携
    template_name = "certification_teams.html"
    # フォームクラス
    form_class = CertificationTeamsForm

    def get_context_data(self, *args, **kwargs):
        context = super(CertificationTeamsView, self).get_context_data(
            *args, **kwargs)
        teams_set = self.get_object()
        team_box = []
        for team in teams_set:
            team_box.append(team)
        context['team_box'] = team_box

        competition_set = self.get_competition_object()
        competition_box = []
        for competition in competition_set:
            competition_box.append(competition)
        context['competition_box'] = competition_box
        data = {}
        for team in teams_set:
            tmp = {}
            for comp in competition_set:
                tmp[comp.title] = f'{team.id}#####{comp.uuid}'

            for comp in CompetitionModel.objects.filter(submissions_teams=team):
                tmp[comp.title] += '_participant'
            data[team.name] = tmp

        context['data'] = data
        return context

    def get_object(self):
        try:
            my_object = TeamTag.objects.all()
            return my_object
        except self.model.DoesNotExist:
            raise Http404(_("No MyModel matches the given query."))

    def get_competition_object(self):
        try:
            my_object = CompetitionModel.objects.filter(
                Q(public=False) | Q(invitation_only=True))# 非公開 or 参加者制限
            return my_object
        except self.model.DoesNotExist:
            raise Http404(_("No MyModel matches the given query."))

    def get_success_url(self):
        return reverse_lazy('manage_users/')

    def post(self, request, *args, **kwargs):
        post_dict = request.POST
        post_dict = dict(request.POST.lists())
        teams_set = self.get_object()
        comp_all = CompetitionModel.objects.all()
        for comp in comp_all:
            comp.submissions_teams.clear()
        for team in teams_set:
            for comp in comp_all:
                for key in post_dict.keys():
                    team_id = key.split('#####')[0]
                    comp_uuid = key.split('#####')[-1]
                    if str(team.id) == team_id and str(comp.uuid) in comp_uuid:
                        status = post_dict.get(key)[0]
                        if status == 'is_participant':
                            t = TeamTag.objects.get(id=team.id)
                            comp.submissions_teams.add(t)
                            comp.save()
  
        self.object = self.get_object()
        self.object_list = self.get_queryset()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        return super(CertificationTeamsView, self).form_valid(form)

    def form_invalid(self, form):
        return super(CertificationTeamsView, self).form_invalid(form)
    
class MakeTeamsView(LoginRequiredMixin,FormMixin, ListView):
    #テーブル連携
    model = TeamTag
    #レコード情報をテンプレートに渡すオブジェクト
    context_object_name = "team_box"
    #テンプレートファイル連携
    template_name = "make_teams.html"
    # フォームクラス
    form_class = MakeTeamForm
    
    object_list = []

    def get_context_data(self, *args, **kwargs):
        context = super(MakeTeamsView, self).get_context_data(*args, **kwargs)
        teams_set = self.get_object()
        users = User.objects.all()
        team_box={}
        for team in teams_set:
            member_data = ""
            for user in users:
                if user.selectedTeam == team:
                    member_data += f"{user.username}, "
                member_data = member_data
            team_box[team.name] = member_data
            
        context['team_box'] = team_box
                
        return context
    
    def get_object(self):
        try:
            my_object = TeamTag.objects.all()
            return my_object
        except self.model.DoesNotExist:
            raise Http404(_("No MyModel matches the given query."))

    def get_success_url(self):
        return reverse_lazy('make_team')

    def post(self, request, *args, **kwargs):
        form = MakeTeamForm(request.POST)
        
        if form.is_valid():
            form.save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        return super(MakeTeamsView, self).form_valid(form)

    def form_invalid(self, form):
        return super(MakeTeamsView, self).form_invalid(form)

class ManageTeamsView(LoginRequiredMixin,FormMixin, ListView):
    #テーブル連携
    model = TeamTag
    user_model = User
    #レコード情報をテンプレートに渡すオブジェクト
    context_object_name = "team_box"
    #テンプレートファイル連携
    template_name = "registration_teams.html"
    # フォームクラス
    form_class = ManageUsersForm

    def get_context_data(self, *args, **kwargs):
        context = super(ManageTeamsView, self).get_context_data(*args, **kwargs)
        
        teams = self.model.objects.all()
        team_box = []
        for team in teams:
            team_box.append(team)
        context['team_box'] = team_box
        
        users = self.user_model.objects.all()
        user_box = []
        for user in users:
            if user.is_staff:
                continue
            user_box.append(user)
            
        context['user_box'] = user_box
        
        return context
    
    def get_object(self):
        try:
            my_object = User.objects.filter(is_staff=False) # スタッフアカウントは操作してはいけない
            return my_object
        except self.model.DoesNotExist:
            raise Http404(_("No MyModel matches the given query."))

    def get_success_url(self):
        return reverse_lazy('manage_users/')

    def post(self, request, *args, **kwargs):
        post_dict = request.POST
        
        team_id = post_dict['main_dropdown']
        team = TeamTag.objects.get(id=team_id)
        
        if "user" in post_dict:
            checked_users = post_dict.getlist('user')
            for user in self.user_model.objects.all():
                if user.username in checked_users:
                    user.selectedTeam = team
                    user.save()
            
        
        self.object = self.get_object()
        self.object_list = self.get_queryset()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        return super(ManageTeamsView, self).form_valid(form)

    def form_invalid(self, form):
        return super(ManageTeamsView, self).form_invalid(form)

class SuspensionUsersView(LoginRequiredMixin,FormMixin, ListView): # 追加
    #テーブル連携
    model = User
    #レコード情報をテンプレートに渡すオブジェクト
    context_object_name = "users_box"
    #テンプレートファイル連携
    template_name = "suspension_users.html"
    # フォームクラス
    form_class = ManageUsersForm

    def get_context_data(self, *args, **kwargs):
        context = super(SuspensionUsersView, self).get_context_data(*args, **kwargs)
        users_set = self.get_object()
        user_box=[]
        for user in users_set:
            user_box.append(user)
        context['user_box'] = user_box
        return context

    def get_object(self):
        try:
            my_object = User.objects.filter(is_staff=False) # スタッフアカウントは操作してはいけない
            return my_object
        except self.model.DoesNotExist:
            raise Http404(_("No MyModel matches the given query."))

    def get_success_url(self):
        return reverse_lazy('manage_users/')

    def post(self, request, *args, **kwargs):
        post_dict = request.POST
        users_set = self.get_object()
        
        update_obj = []
        for user in users_set:
            u_pk = user.pk
            status = post_dict.getlist(str(u_pk))[0]
            if status == 'is_active':
                user.is_active = True
            else:
                user.is_active = False
            update_obj.append(user)
        
        User.objects.bulk_update(update_obj, fields=['is_active'])  # ここで更新クエリ1つ発行
        # 形骸
        self.object = self.get_object()
        self.object_list = self.get_queryset()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        return super(SuspensionUsersView, self).form_valid(form)

    def form_invalid(self, form):
        return super(SuspensionUsersView, self).form_invalid(form)

class RegistrationUsersView(LoginRequiredMixin,FormMixin, ListView): # 追加
    #テーブル連携
    model = User
    #レコード情報をテンプレートに渡すオブジェクト
    context_object_name = "users_box"
    #テンプレートファイル連携
    template_name = "registration_users.html"
    # フォームクラス
    form_class = ManageUsersForm

    def get_context_data(self, *args, **kwargs):
        context = super(RegistrationUsersView, self).get_context_data(*args, **kwargs)
        users_set = self.get_object()
        user_box=[]
        for user in users_set:
            user_box.append(user)
        context['user_box'] = user_box
        
        return context

    def get_object(self):
        try:
            my_object = User.objects.filter(is_staff=False) # スタッフアカウントは操作してはいけない
            return my_object
        except self.model.DoesNotExist:
            raise Http404(_("No MyModel matches the given query."))

    def get_success_url(self):
        return reverse_lazy('manage_users/')

    def post(self, request, *args, **kwargs):
        post_dict = request.POST
        users_set = self.get_object()
        # is_participant 参加認証
        upd_obj = []
        for user in users_set:
            u_pk = user.pk
            status = post_dict.getlist(str(u_pk))[0]
            if status == 'is_participant':
                user.is_participant=True
            else:
                user.is_participant=False
            upd_obj.append(user)
        User.objects.bulk_update(upd_obj, fields=['is_participant'])  # ここで更新クエリ1つ発行
        # 形骸
        self.object = self.get_object()
        self.object_list = self.get_queryset()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        return super(RegistrationUsersView, self).form_valid(form)

    def form_invalid(self, form):
        return super(RegistrationUsersView, self).form_invalid(form)

class EditConfigBoxView(LoginRequiredMixin, UpdateView):  # 追加
    """「全体設定」ページ、実際には認証コード設定のみ."""

    model = ConfigBox
    form_class = EditConfigBoxForm
    template_name = 'edit_config.html'
    success_url = 'edit_config.html'

    def get_success_url(self):
        return reverse_lazy('edit_config', kwargs={'pk': self.object.pk})

    def get_object(self):
        try:
            my_object = ConfigBox.objects.get(id=1)
            return my_object
        except self.model.DoesNotExist:
            raise Http404(_("No MyModel matches the given query."))

    def get_context_data(self, *args, **kwargs):
        context = super(EditConfigBoxView,
                        self).get_context_data(*args, **kwargs)
        return context

    def post(self, request, *args, **kwargs):
        print(request.POST)
        self.object = self.get_object()
        form = self.get_form()
        if not (request.user.is_staff or request.user.is_superuser):
            raise PermissionDenied()
        if form.is_valid():
            authentication_code = request.POST.get('authentication_code')
            
            self.object.authentication_code = authentication_code
            self.object.save()

            # TODO: 変更対象、変更内容を記録する
            msg = f"{_('設定を変更しました')}"
            logger.info(msg, extra={
                'request': self.request,
                'action': {
                    'name': 'configure',
                    'is_valid': True,
                    }
                })
            return self.form_valid(form)
        else:
            msg = f"{_('フォームの入力内容が不正です')}"
            logger.error(msg, extra={
                'request': self.request,
                'action': {
                    'name': 'configure',
                    'is_valid': False,
                    }
                })
            return self.form_invalid(form)

    def form_valid(self, form):
        return super(EditConfigBoxView, self).form_valid(form)

    def form_invalid(self, form):
        return super(EditConfigBoxView, self).form_invalid(form)
