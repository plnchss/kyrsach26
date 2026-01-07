from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter
from .viewsets import VotingViewSet, NominationViewSet, ParticipantViewSet, VoteViewSet
from .views import VotingViewSet, NominationViewSet, ParticipantViewSet, VoteViewSet

router = DefaultRouter()
router.register(r"votings", VotingViewSet)
router.register(r"nominations", NominationViewSet)
router.register(r"participants", ParticipantViewSet)
router.register(r"votes", VoteViewSet)

urlpatterns = [
    path('', views.index, name='index'),  
    path('voting/<int:voting_id>/', views.voting_detail, name='voting_detail'),
    path('vote/<int:participant_id>/', views.vote, name='vote'),
    path('login/', auth_views.LoginView.as_view(template_name='voting/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('register/', views.register, name='register'),
    path('unvote/<int:participant_id>/', views.unvote, name='unvote'),
    path("api/", include(router.urls)),
    path('', include(router.urls)),
]
