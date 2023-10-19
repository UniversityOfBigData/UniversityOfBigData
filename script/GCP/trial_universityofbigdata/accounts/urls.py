from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from accounts import views

#app_name ="accunts"

urlpatterns = [
    path('ProfileEdit/', views.ProfileEditView.as_view(), name='profileedit'),
    path('signup/', views.ProfileRegistrationView.as_view(), name='signup'),
    path('signup_google/', views.ProfileRegistrationGoogleView.as_view(), name='signup_google'),
]
