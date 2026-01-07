# voting/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.utils.timezone import now
from django.core.paginator import Paginator
from .models import Voting, Participant, Vote

# ------------------ Веб-интерфейс ------------------
def index(request):
    """Главная страница: список всех голосований с пагинацией"""
    votings_list = Voting.objects.all().order_by("-created_at")
    paginator = Paginator(votings_list, 12)  # 12 карточек на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'voting/index.html', {'page_obj': page_obj})

def voting_detail(request, voting_id):
    """Детальная страница голосования с участниками и текущими голосами пользователя"""
    voting = get_object_or_404(Voting, pk=voting_id)
    user_votes = {}

    if request.user.is_authenticated:
        votes = Vote.objects.filter(
            user=request.user,
            participant__nomination__voting=voting
        )
        for vote in votes:
            user_votes[vote.participant.nomination.id] = vote.participant.id

    return render(request, 'voting/detail.html', {
        'voting': voting,
        'user_votes': user_votes,
    })

@login_required
def vote(request, participant_id):
    """Голосование за участника"""
    participant = get_object_or_404(Participant, pk=participant_id)
    nomination = participant.nomination

    existing_vote = Vote.objects.filter(
        user=request.user,
        participant__nomination=nomination
    ).first()

    if not existing_vote:
        Vote.objects.create(user=request.user, participant=participant)

    return redirect('voting_detail', voting_id=nomination.voting.id)

@login_required
def unvote(request, participant_id):
    """Отмена голоса за участника"""
    participant = get_object_or_404(Participant, pk=participant_id)
    Vote.objects.filter(
        user=request.user,
        participant__nomination=participant.nomination
    ).delete()
    return redirect('voting_detail', voting_id=participant.nomination.voting.id)

def register(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'voting/register.html', {'form': form})

# ------------------ DRF API ------------------
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import VotingSerializer, NominationSerializer, ParticipantSerializer, VoteSerializer
from .models import Voting, Nomination, Participant, Vote

# ---------------- VotingViewSet ----------------
class VotingViewSet(viewsets.ModelViewSet):
    """API для голосований"""
    queryset = Voting.objects.all().order_by("-created_at")
    serializer_class = VotingSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["start_date", "end_date"]
    search_fields = ["title", "description"]
    ordering_fields = ["start_date", "end_date", "created_at"]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Список активных голосований"""
        active_votings = Voting.objects.filter(start_date__lte=now(), end_date__gte=now())
        serializer = self.get_serializer(active_votings, many=True)
        return Response(serializer.data)

# ---------------- NominationViewSet ----------------
class NominationViewSet(viewsets.ModelViewSet):
    """API для номинаций"""
    queryset = Nomination.objects.all()
    serializer_class = NominationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["voting"]
    search_fields = ["title", "description"]
    ordering_fields = ["title"]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

# ---------------- ParticipantViewSet ----------------
class ParticipantViewSet(viewsets.ModelViewSet):
    """API для участников"""
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["nomination", "nomination__voting"]
    search_fields = ["name", "description"]
    ordering_fields = ["name"]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

# ---------------- VoteViewSet ----------------
class VoteViewSet(viewsets.ModelViewSet):
    """API для голосов"""
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["participant", "participant__nomination", "participant__nomination__voting"]
    ordering_fields = ["voted_at"]

    def get_queryset(self):
        """Показываем пользователю только его голоса"""
        return Vote.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Создаем голос с текущим пользователем"""
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Последние 10 голосов текущего пользователя"""
        votes = self.get_queryset().order_by('-voted_at')[:10]
        serializer = self.get_serializer(votes, many=True)
        return Response(serializer.data)
