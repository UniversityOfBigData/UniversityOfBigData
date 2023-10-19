from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('login/', LoginView.as_view(redirect_authenticated_user=True, template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]