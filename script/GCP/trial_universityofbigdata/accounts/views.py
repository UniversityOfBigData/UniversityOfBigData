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
    success_url = '/universityofbigdata/login_required/'
    
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
    form_class = ProfileForm
    success_url = '/universityofbigdata/login_required/'
    
    def get_object(self):
        return self.request.user

    def get_initial(self):
        initial = super().get_initial()
        if(self.request.user.nickname is None or self.request.user.nickname == ""):
            self.request.user.nickname = self.request.user.username
        return initial

# def MyPage(request):
#     # 'HTTP_X_FORWARDED_FOR'ヘッダから転送経路のIPアドレスを取得
#     forwarded_addresses = request.META.get('HTTP_X_FORWARDED_FOR')
#     if forwarded_addresses:
#         # 'HTTP_X_FORWARDED_FOR'ヘッダがある場合は転送経路の先頭要素を取得
#         client_ip = forwarded_addresses.split(',')[0]
#     else:
#         # 'HTTP_X_FORWARDED_FOR'ヘッダがない場合は'REMOTE_ADDR'ヘッダを参照
#         client_ip = request.META.get('REMOTE_ADDR')
#     # 所属チームの取得
#     team_tag_query_set = request.user.team_tags.all()
#     box=[]
#     t_box=[]
#     for tg in team_tag_query_set:
#         t_box.append(tg)
#         box.append(tg.name)
#     team_tags = box
#     return render(request, 'accounts/mypage.html', {'client_ip':client_ip, 'team_tags':team_tags})


# def TeamPage(request):
#     username=request.user.username
#     team_tag_query_set = request.user.team_tags.all()

#     box=[]
#     t_box=[]
#     for tg in team_tag_query_set:
#         t_box.append(tg)
#         box.append(tg.name)
#     team_tags = box

#     # 表示チームの選択処理ができるといいな
#     if request.method == 'POST':
#         print('x')
#         team_tag=team_tags[0]
#         t=t_box[0]
#     else:
#         #team_tag=team_tags[0]
#         team_tag = request.user.selectedTeam
#         t=t_box[0]

#     m=t.member_data
#     if(m == None):
#         print(m)
#         t.save()
#         m=t.member_data
#         member_list=m.split(',')
#     else:
#         member_list=m.split(',')

#     logger = logging.getLogger(__name__)
#     msg='look TeamPage'+str(team_tag)+','+str(username)
#     logger.info(msg)

#     log=t.logs_data
#     if log is None:
#         log=''
#     logs_data=log.split(',')
#     logs_data.append(msg)
#     logs_data.append('end')

#     context = {
#         'username':username,
#         'team_tag_list':team_tags,
#         'team_tag':team_tag,
#         'member_list':member_list,
#         'logs_data':logs_data,
#     }
#     return render(request, 'team/teampage.html', context)
