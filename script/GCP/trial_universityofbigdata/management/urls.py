from django.urls import path

from management import views

urlpatterns = [
    path('competitions_create/', views.CompetitionsCreateView.as_view(), name='competitions_create'),
    path('certification_teams/',views.CertificationTeamsView.as_view(), name='certification_teams'),
    path('make_team/', views.MakeTeamsView.as_view(), name='make_team'),
    path('manage_teams/', views.ManageTeamsView.as_view(), name='manage_teams'),
    path('suspension_users/', views.SuspensionUsersView.as_view(), name='suspension_users'),
    path('registration_users/', views.RegistrationUsersView.as_view(), name='registration_users'),
    path('edit_config/<int:pk>', views.EditConfigBoxView.as_view(), name='edit_config'),
]