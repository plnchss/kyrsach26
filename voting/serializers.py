from rest_framework import serializers
from .models import Voting, Nomination, Participant, Vote
from django.utils.timezone import now

# ---------------- Voting Serializer ----------------
class VotingSerializer(serializers.ModelSerializer):
    nominations = serializers.StringRelatedField(many=True, read_only=True)
    is_active = serializers.ReadOnlyField()

    class Meta:
        model = Voting
        fields = [
            "id", "title", "description", 
            "start_date", "end_date", 
            "created_at", "updated_at", 
            "is_active", "nominations"
        ]

    def validate(self, data):
        start_date = data.get("start_date", getattr(self.instance, "start_date", None))
        end_date = data.get("end_date", getattr(self.instance, "end_date", None))
        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError("Дата начала должна быть раньше даты окончания")
        return data

# ---------------- Nomination Serializer ----------------
class NominationSerializer(serializers.ModelSerializer):
    voting_title = serializers.ReadOnlyField(source="voting.title")
    participants_count = serializers.SerializerMethodField()

    class Meta:
        model = Nomination
        fields = ["id", "title", "description", "voting", "voting_title", "participants_count"]

    def get_participants_count(self, obj):
        return obj.participants.count()

# ---------------- Participant Serializer ----------------
class ParticipantSerializer(serializers.ModelSerializer):
    nomination_title = serializers.ReadOnlyField(source="nomination.title")
    votes_count = serializers.ReadOnlyField(source="votes.count")
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = Participant
        fields = ["id", "name", "description", "nomination", "nomination_title", "avatar_url", "votes_count"]

    def get_avatar_url(self, obj):
        if obj.avatar:
            request = self.context.get("request")
            return request.build_absolute_uri(obj.avatar.url) if request else obj.avatar.url
        return None

# ---------------- Vote Serializer ----------------
class VoteSerializer(serializers.ModelSerializer):
    participant_name = serializers.ReadOnlyField(source="participant.name")
    nomination_id = serializers.ReadOnlyField(source="participant.nomination.id")

    class Meta:
        model = Vote
        fields = ["id", "user", "participant", "participant_name", "nomination_id", "voted_at"]
        read_only_fields = ["user", "voted_at"]

    def validate(self, attrs):
        user = self.context["request"].user
        participant = attrs["participant"]

        if Vote.objects.filter(user=user, participant__nomination=participant.nomination).exists():
            raise serializers.ValidationError("Вы уже голосовали в этой номинации")
        return attrs

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
