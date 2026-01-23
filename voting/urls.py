from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, viewsets

# Настройка API роутера
router = DefaultRouter()
router.register(r'votings', viewsets.VotingViewSet)
router.register(r'nominations', viewsets.NominationViewSet)
router.register(r'participants', viewsets.ParticipantViewSet)
router.register(r'votes', viewsets.VoteViewSet)

urlpatterns = [
    # Веб-интерфейс (HTML)
    path('', views.index, name='index'),
    path('voting/<int:voting_id>/', views.voting_detail, name='voting_detail'),
    path('vote/<int:participant_id>/', views.vote, name='vote'),
    path('unvote/<int:participant_id>/', views.unvote, name='unvote'),
    path('register/', views.register, name='register'),
    path('accounts/', include('django.contrib.auth.urls')), # Для входа/выхода

    # API
    path('api/', include(router.urls)),
]