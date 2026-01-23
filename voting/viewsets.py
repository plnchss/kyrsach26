from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.utils.timezone import now
from django_filters.rest_framework import DjangoFilterBackend
from .models import Voting, Nomination, Participant, Vote
from .serializers import VotingSerializer, NominationSerializer, ParticipantSerializer, VoteSerializer

class VotingViewSet(viewsets.ModelViewSet):
    queryset = Voting.objects.all()
    serializer_class = VotingSerializer
    # Настройка фильтрации для пункта №4 и №5 ТЗ
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['title', 'start_date'] # Фильтр по полям
    search_fields = ['title', 'description']    # Поиск по названию/описанию

    # 1. Action: Список активных (detail=False)
    @action(methods=['GET'], detail=False)
    def active(self, request):
        active_votings = Voting.objects.filter(end_date__gte=now())
        serializer = self.get_serializer(active_votings, many=True)
        return Response(serializer.data)

    # 2. Action: Закрыть вручную (detail=True) - ТРЕБОВАНИЕ №6
    @action(methods=['POST'], detail=True)
    def close(self, request, pk=None):
        voting = self.get_object()
        voting.end_date = now()
        voting.save()
        return Response({'status': 'Голосование закрыто'})

    # 3. МЕГА-ПОИСК (Q-объекты: И, ИЛИ, НЕ) - ТРЕБОВАНИЕ НА "ХОРОШО"
    @action(methods=['GET'], detail=False)
    def mega_search(self, request):
        query = request.query_params.get('q', '')
        # (Заголовок содержит Q ИЛИ описание содержит Q) И заголовок НЕ содержит 'архив'
        results = Voting.objects.filter(
            (Q(title__icontains=query) | Q(description__icontains=query)) & 
            ~Q(title__icontains='архив')
        )
        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)

class NominationViewSet(viewsets.ModelViewSet):
    queryset = Nomination.objects.all()
    serializer_class = NominationSerializer

class ParticipantViewSet(viewsets.ModelViewSet):
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer

    # Доп. метод для лидеров
    @action(methods=['GET'], detail=False)
    def popular(self, request):
        from django.db.models import Count
        popular_list = Participant.objects.annotate(v_count=Count('votes')).order_by('-v_count')
        serializer = self.get_serializer(popular_list, many=True)
        return Response(serializer.data)

class VoteViewSet(viewsets.ModelViewSet):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer

    # Фильтрация по текущему пользователю - ТРЕБОВАНИЕ НА "ОТЛИЧНО"
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Vote.objects.filter(user=user)
        return Vote.objects.none()