from django.shortcuts import render
from django.http import Http404
from django.db.models import Q
from django.views.generic.edit import CreateView, UpdateView, FormMixin  # 追加 # 追加
from .forms import (ProfileForm, SetProfileForm)   # 追加
from django.views.generic import ListView # 追加
from django.contrib.auth.mixins import LoginRequiredMixin # 追加
from .models import User, TeamTag # 追加
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
import logging

logger = logging.getLogger(__name__)


class ProfileEditView(LoginRequiredMixin, UpdateView): # 追加
    template_name = 'accounts/edit_profile.html'
    model = User
    form_class = ProfileForm
    success_url = '/'
    
    def get_object(self):
        return self.request.user

class ProfileRegistrationView(CreateView): # 追加
    template_name = 'accounts/registration_profile.html'
    model = User
    form_class = SetProfileForm
    success_url = '/authentication/login_required/'
    
    def get_object(self):
        return self.request.user

    def get_initial(self):
        initial = super().get_initial()
        if(
            not hasattr(self.request.user, 'nickname')
                or self.request.user.nickname is None
                or self.request.user.nickname == ""
        ):
            self.request.user.nickname = self.request.user.username
        return initial

class ProfileRegistrationGoogleView(LoginRequiredMixin, UpdateView): # 追加
    template_name = 'accounts/registration_profile_google.html'
    model = User
    teamtag = TeamTag
    form_class = ProfileForm
    success_url = '/authentication/login_required/'
    
    def get_object(self):
        return self.request.user

    def get_initial(self):
        initial = super().get_initial()
        if(self.request.user.nickname is None or self.request.user.nickname == ""):
            self.request.user.nickname = self.request.user.username
        return initial
    
    def post(self, request, *args, **kwargs):
        # ログインしたユーザのチーム登録がなかったら
        # ユーザ名と同じチームを作成し登録
        self.object = self.get_object()
        if request.user.selectedTeam is None:
            team = TeamTag(name=request.user.username)
            team.save()
            
            request.user.selectedTeam = team
            request.user.save()
            
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

        return render(request, self.template_name, context=self.kwargs)
    
    def form_valid(self, form):
        return super(ProfileRegistrationGoogleView, self).form_valid(form)

    def form_invalid(self, form):
        return super(ProfileRegistrationGoogleView, self).form_invalid(form)
