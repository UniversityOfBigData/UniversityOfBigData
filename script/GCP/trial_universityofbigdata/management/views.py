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

from universityofbigdata.lib.mylogger import set_log_box_lite

logger = logging.getLogger(__name__)

# Create your views here.

class CompetitionsCreateView(LoginRequiredMixin, CreateView):
    model = CompetitionModel
    form_class = CompetitionForm
    template_name = 'competitions_create.html'
    success_url = '/'
    
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
        c_box=[]
        for team_p in team_box:
            c_dict={}
            b_box=[]
            c_set = CompetitionModel.objects.filter(submissions_teams=team_p)
            for c in c_set:
                b_box.append(c.id)
            c_dict['team']=team_p
            c_dict['mix_box']=b_box
            c_box.append(c_dict)
        context['mix_box'] = c_box
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
        comp_dict ={}
        for team in teams_set:
            competition_allow_box = post_dict.get(str(team.pk))
            if not(competition_allow_box is None):
                for comp_id in competition_allow_box:
                    box=comp_dict.get(str(comp_id))
                    if (box is None):
                        box=[team.id]
                    else:
                        box.append(team.id)
                    comp_dict[str(comp_id)]=box
        # クリアー
        comp_all = CompetitionModel.objects.all()
        for comp in comp_all:
            comp.submissions_teams.clear()
        for key in comp_dict.keys():
            add_team_box = comp_dict[key]
            comp = CompetitionModel.objects.get(id=int(key))
            for team_id in add_team_box:
                t = TeamTag.objects.get(id=team_id)
                comp.submissions_teams.add(t)
            comp.save()
        # 形骸
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

    def get_context_data(self, *args, **kwargs):
        context = super(MakeTeamsView, self).get_context_data(*args, **kwargs)
        teams_set = self.get_object()
        team_box=[]
        for team in teams_set:
            team_box.append(team)
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
        post_obj=form.save()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        return super(MakeTeamsView, self).form_valid(form)

    def form_invalid(self, form):
        return super(MakeTeamsView, self).form_invalid(form)

class ManageTeamsView(LoginRequiredMixin,FormMixin, ListView):
    #テーブル連携
    model = User
    #レコード情報をテンプレートに渡すオブジェクト
    context_object_name = "users_box"
    #テンプレートファイル連携
    template_name = "registration_teams.html"
    # フォームクラス
    form_class = ManageUsersForm

    def get_context_data(self, *args, **kwargs):
        context = super(ManageTeamsView, self).get_context_data(*args, **kwargs)
        users_set = self.get_object()
        user_box=[]
        for user in users_set:
            user_box.append(user)
        context['user_box'] = user_box
        teams_set = self.get_team_object()
        team_box=[]
        for team in teams_set:
            team_box.append(team)
        context['team_box'] = team_box
        return context
    
    def get_team_object(self):
        try:
            my_object = TeamTag.objects.all()
            return my_object
        except self.model.DoesNotExist:
            raise Http404(_("No MyModel matches the given query."))

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
        teams_set = self.get_team_object()
        upd_obj = []
        for user in users_set:
            u_pk = user.pk
            post_obj = post_dict.getlist(str(u_pk))
            for team in teams_set:
                if(str(team.pk) in post_obj):
                    user.selectedTeam=team
                    team_set = user.team_tags.all()
                    pk_box=[]
                    for team_p in team_set:
                        pk_box.append(team_p.pk)
                    if not(team.pk in pk_box):
                        user.team_tags.add(team)
            upd_obj.append(user)
        User.objects.bulk_update(upd_obj, fields=['selectedTeam'])  # ここで更新クエリ1つ発行
        # 形骸
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
        # is_participant 参加認証
        post_box = post_dict.getlist('is_participant')
        upd_obj = []
        for user in users_set:
            u_pk = user.pk
            if(str(u_pk) in post_box):
                user.is_participant=True
            else:
                user.is_participant=False
            upd_obj.append(user)
        User.objects.bulk_update(upd_obj, fields=['is_participant'])  # ここで更新クエリ1つ発行
        # ユーザの有効無効
        post_box = post_dict.getlist('is_active')
        upd_obj = []
        for user in users_set:
            u_pk = user.pk
            if(str(u_pk) in post_box):
                user.is_active=True
            else:
                user.is_active=False
            upd_obj.append(user)
        User.objects.bulk_update(upd_obj, fields=['is_active'])  # ここで更新クエリ1つ発行
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
        post_box = post_dict.getlist('is_participant')
        upd_obj = []
        for user in users_set:
            u_pk = user.pk
            if(str(u_pk) in post_box):
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
        # logging
        message = set_log_box_lite(
            'Competition Discussion Post successful', self.request)
        logger.info(message)
        return reverse_lazy('edit_config', kwargs={'pk': self.object.pk})

    def get_object(self):
        try:
            my_object = ConfigBox.objects.get(name='signInCode')
            return my_object
        except self.model.DoesNotExist:
            raise Http404(_("No MyModel matches the given query."))

    def get_context_data(self, *args, **kwargs):
        context = super(EditConfigBoxView,
                        self).get_context_data(*args, **kwargs)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if not (request.user.is_staff or request.user.is_superuser):
            raise PermissionDenied()
        if form.is_valid():
            authentication_code = request.POST.get('authentication_code')
            # name = request.POST.get('name')
            self.object.authentication_code = authentication_code
            self.object.save()
            return self.form_valid(form)
        else:
            # print('is_invalid')
            return self.form_invalid(form)

    def form_valid(self, form):
        return super(EditConfigBoxView, self).form_valid(form)

    def form_invalid(self, form):
        return super(EditConfigBoxView, self).form_invalid(form)