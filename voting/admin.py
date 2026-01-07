from django.contrib import admin
from import_export.admin import ExportMixin
from .models import Voting, Nomination, Participant, Vote

# -------------------- Inlines --------------------
class NominationInline(admin.TabularInline):
    model = Nomination
    extra = 1


class ParticipantInline(admin.TabularInline):
    model = Participant
    extra = 1
    autocomplete_fields = ("nomination",)


# -------------------- Voting --------------------
@admin.register(Voting)
class VotingAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ("id", "title", "start_date", "end_date", "created_at", "is_active")
    list_filter = ("start_date", "end_date")
    date_hierarchy = "start_date"
    inlines = [NominationInline]
    search_fields = ("title",)
    list_display_links = ("id", "title")

    @admin.display(boolean=True, description="Активно")
    def is_active(self, obj):
        return obj.is_active


# -------------------- Nomination --------------------
@admin.register(Nomination)
class NominationAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ("id", "title", "voting", "participants_count")
    list_filter = ("voting",)
    inlines = [ParticipantInline]
    search_fields = ("title",)
    list_display_links = ("id", "title")

    @admin.display(description="Количество участников")
    def participants_count(self, obj):
        return obj.participants.count()


# -------------------- Participant --------------------
@admin.register(Participant)
class ParticipantAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ("id", "name", "nomination", "votes_count", "created_at")
    list_filter = ("nomination", "nomination__voting")
    search_fields = ("name", "nomination__title", "nomination__voting__title")
    autocomplete_fields = ("nomination",)

    @admin.display(description="Количество голосов")
    def votes_count(self, obj):
        return obj.votes.count()


# -------------------- Vote --------------------
@admin.register(Vote)
class VoteAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ("id", "user", "participant", "voted_at")
    list_filter = ("voted_at", "participant__nomination__voting")
    date_hierarchy = "voted_at"
    search_fields = ("user__username", "participant__name", "participant__nomination__title")
    autocomplete_fields = ("participant", "user")
