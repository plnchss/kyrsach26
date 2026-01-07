# voting/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Voting, Participant, Vote
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

# ------------------ Веб-интерфейс ------------------
def index(request):
    votings = Voting.objects.all()
    return render(request, 'voting/index.html', {'votings': votings})

def voting_detail(request, voting_id):
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
    participant = get_object_or_404(Participant, pk=participant_id)
    Vote.objects.filter(
        user=request.user,
        participant__nomination=participant.nomination
    ).delete()
    return redirect('voting_detail', voting_id=participant.nomination.voting.id)

def register(request):
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
from .serializers import VotingSerializer, NominationSerializer, ParticipantSerializer, VoteSerializer
from .models import Voting, Nomination, Participant, Vote
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.timezone import now

class VotingViewSet(viewsets.ModelViewSet):
    queryset = Voting.objects.all()
    serializer_class = VotingSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["start_date", "end_date"]
    search_fields = ["title", "description"]
    ordering_fields = ["start_date", "end_date", "created_at"]

    @action(methods=['get'], detail=False)
    def active(self, request):
        active_votings = Voting.objects.filter(start_date__lte=now(), end_date__gte=now())
        serializer = self.get_serializer(active_votings, many=True)
        return Response(serializer.data)

class NominationViewSet(viewsets.ModelViewSet):
    queryset = Nomination.objects.all()
    serializer_class = NominationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["voting"]
    search_fields = ["title"]

class ParticipantViewSet(viewsets.ModelViewSet):
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["nomination", "nomination__voting"]
    search_fields = ["name"]

class VoteViewSet(viewsets.ModelViewSet):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["participant", "participant__nomination__voting"]

    def get_queryset(self):
        return Vote.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(methods=['get'], detail=False)
    def recent(self, request):
        votes = self.get_queryset().order_by('-voted_at')[:10]
        serializer = self.get_serializer(votes, many=True)
        return Response(serializer.data)
