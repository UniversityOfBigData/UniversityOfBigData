from django.urls import path
from discussion import views

app_name = "Discussion"

urlpatterns = [
    path('discussion_competition/<int:pk>', views.DiscussionCompetitionView.as_view(), name='discussion_competition'),
    path('discussion_post/<int:pk>', views.DiscussionPostView.as_view(), name='discussion_post'),
]
