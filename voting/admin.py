from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from import_export.admin import ExportMixin
from .models import Voting, Nomination, Participant, Vote
from .resources import VotingResource

class NominationInline(admin.TabularInline):
    model = Nomination
    extra = 0

class ParticipantInline(admin.TabularInline):
    model = Participant
    extra = 1 # Сколько пустых строк для новых участников показать сразу

@admin.register(Voting)
class VotingAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = VotingResource
    list_display = ("title", "start_date", "end_date", "display_status")
    list_filter = ("start_date", "end_date")
    inlines = [NominationInline]
    search_fields = ("title",)

    def display_status(self, obj):
        if obj.is_active:
            return format_html('<b style="color: green;">Активно</b>')
        return format_html('<b style="color: red;">Завершено</b>')
    display_status.short_description = "Статус"

@admin.register(Nomination)
class NominationAdmin(admin.ModelAdmin):
    list_display = ('title', 'voting')
    inlines = [ParticipantInline] # участники внутри номинации

@admin.register(Participant)
class ParticipantAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ("name", "link_to_nomination", "votes_count")
    
    def link_to_nomination(self, obj):
        link = reverse("admin:voting_nomination_change", args=[obj.nomination.id])
        return format_html('<a href="{}">{}</a>', link, obj.nomination.title)
    link_to_nomination.short_description = "Номинация"

    def votes_count(self, obj):
        return obj.votes.count()
    votes_count.short_description = "Голосов"

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ("user", "participant", "voted_at")
    raw_id_fields = ("user", "participant") # удобный выбор ID