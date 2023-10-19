from django.urls import path

from userlog import views

urlpatterns = [
    path('log_listview/', views.LogBoxListView.as_view(), name='log_listview'),
    path('management_log_listview/', views.ManagementLogBoxListView.as_view(), name='management_log_listview'),
]