from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.timezone import now
from .models import Voting, Nomination, Participant, Vote
from .serializers import VotingSerializer, NominationSerializer, ParticipantSerializer, VoteSerializer
from .permissions import IsOwnerOrReadOnly

# ---------------------------- Voting ----------------------------
class VotingViewSet(viewsets.ModelViewSet):
    queryset = Voting.objects.all().order_by("-created_at")
    serializer_class = VotingSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["start_date", "end_date"]
    search_fields = ["title", "description"]
    ordering_fields = ["start_date", "end_date", "created_at"]
    ordering = ["-created_at"]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # ---------------------- Custom Actions ----------------------
    @action(detail=False, methods=['get'], url_path='expired')
    def expired_votings(self, request):
        """Возвращает все голосования, которые уже завершились"""
        expired = Voting.objects.filter(end_date__lt=now())
        serializer = self.get_serializer(expired, many=True)
        return Response(serializer.data)

# ---------------------------- Nomination ----------------------------
class NominationViewSet(viewsets.ModelViewSet):
    queryset = Nomination.objects.all()
    serializer_class = NominationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["voting"]
    search_fields = ["title", "description"]
    ordering_fields = ["title"]
    ordering = ["title"]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

# ---------------------------- Participant ----------------------------
class ParticipantViewSet(viewsets.ModelViewSet):
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["nomination", "nomination__voting"]
    search_fields = ["name", "description", "nomination__title", "nomination__voting__title"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # ---------------------- Custom Actions ----------------------
    @action(detail=False, methods=['get'], url_path='popular')
    def popular_participants(self, request):
        """
        Возвращает участников с наибольшим количеством голосов
        """
        popular = sorted(self.get_queryset(), key=lambda p: p.votes_count(), reverse=True)[:10]
        serializer = self.get_serializer(popular, many=True, context={'request': request})
        return Response(serializer.data)

# ---------------------------- Vote ----------------------------
class VoteViewSet(viewsets.ModelViewSet):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["user", "participant", "participant__nomination"]
    search_fields = ["user__username", "participant__name", "participant__nomination__title"]
    ordering_fields = ["voted_at"]
    ordering = ["-voted_at"]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # ---------------------- Custom Actions ----------------------
    @action(detail=False, methods=['get'], url_path='history')
    def my_vote_history(self, request):
        """
        История голосов текущего пользователя
        """
        votes = Vote.objects.filter(user=request.user).order_by('-voted_at')
        serializer = self.get_serializer(votes, many=True)
        return Response(serializer.data)
