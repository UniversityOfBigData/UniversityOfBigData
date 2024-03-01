from django.contrib.auth.views import LogoutView
from django.urls import path
from django.utils.translation import gettext_lazy as _
from accounts import views
from universityofbigdata.utils import access_recorded


urlpatterns = [
    path('ProfileEdit/', views.ProfileEditView.as_view(), name='profileedit'),
    path('signup/', views.ProfileRegistrationView.as_view(), name='signup'),
    path('signup_google/', views.ProfileRegistrationGoogleView.as_view(),
        name='signup_google'),
]
