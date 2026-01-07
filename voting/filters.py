# voting/filters.py
from django_filters import rest_framework as filters
from django.utils.timezone import now
from .models import Voting, Nomination, Participant, Vote

# ---------------- Voting Filter ----------------
class VotingFilter(filters.FilterSet):
    active = filters.BooleanFilter(method='filter_active')
    expired = filters.BooleanFilter(method='filter_expired')
    title = filters.CharFilter(field_name='title', lookup_expr='icontains')

    class Meta:
        model = Voting
        fields = ['start_date', 'end_date', 'title']

    def filter_active(self, queryset, name, value):
        if value:
            return queryset.filter(start_date__lte=now(), end_date__gte=now())
        return queryset

    def filter_expired(self, queryset, name, value):
        if value:
            return queryset.filter(end_date__lt=now())
        return queryset

# ---------------- Nomination Filter ----------------
class NominationFilter(filters.FilterSet):
    voting_title = filters.CharFilter(field_name='voting__title', lookup_expr='icontains')
    min_participants = filters.NumberFilter(method='filter_min_participants')

    class Meta:
        model = Nomination
        fields = ['voting', 'title']

    def filter_min_participants(self, queryset, name, value):
        return queryset.annotate(num=filters.Count('participants')).filter(num__gte=value)

# ---------------- Participant Filter ----------------
class ParticipantFilter(filters.FilterSet):
    nomination_title = filters.CharFilter(field_name='nomination__title', lookup_expr='icontains')
    min_votes = filters.NumberFilter(method='filter_min_votes')

    class Meta:
        model = Participant
        fields = ['nomination', 'name']

    def filter_min_votes(self, queryset, name, value):
        return queryset.annotate(num=filters.Count('votes')).filter(num__gte=value)

# ---------------- Vote Filter ----------------
class VoteFilter(filters.FilterSet):
    nomination = filters.NumberFilter(field_name='participant__nomination')
    voting = filters.NumberFilter(field_name='participant__nomination__voting')

    class Meta:
        model = Vote
        fields = ['user', 'participant', 'nomination', 'voting']
