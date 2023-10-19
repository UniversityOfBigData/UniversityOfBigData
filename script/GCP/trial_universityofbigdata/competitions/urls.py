from django.urls import path
from competitions import views

app_name = "Competitions"

urlpatterns = [
    path('competitions_list/', views.CompetitionsListView.as_view(), name='competitions_list'),
    path('competitions_main/<int:pk>', views.CompetitionsMainView.as_view(), name='competitions_main'),
    path('competitions_data/<int:pk>', views.CompetitionsDataView.as_view(), name='competitions_data'),
    path('competitions_post/<int:pk>', views.CompetitionsPostView.as_view(), name='competitions_post'),
    path('competitions_ranking/<int:pk>', views.CompetitionsRankingView.as_view(), name='competitions_ranking'),
]
