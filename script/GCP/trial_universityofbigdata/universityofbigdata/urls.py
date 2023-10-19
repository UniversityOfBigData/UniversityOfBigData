from django.urls import path
from universityofbigdata import views

urlpatterns = [
    path('participation_guide/', views.participation_guide , name='participation_guide'),# 参加案内
    path('login_required/', views.login_required, name='login_required'),
    path('login_google/', views.LoginView, name='login_google'),
]