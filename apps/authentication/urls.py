from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from django.utils.translation import gettext_lazy as _
from universityofbigdata.utils import access_recorded
from authentication import views
from authentication.views import logger

urlpatterns = [
    path('login/', access_recorded(logger, 'login', _('ログインページ'))(
        LoginView.as_view(
            redirect_authenticated_user=True, template_name='login.html')
        ), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('participation_guide/', access_recorded(
        logger, 'participation_guide', _('参加案内ページ'))(
        views.participation_guide), name='participation_guide'),
    path('login_required/', views.login_required, name='login_required'),
]
