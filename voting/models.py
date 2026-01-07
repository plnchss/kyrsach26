from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from simple_history.models import HistoricalRecords


class Voting(models.Model):
    title = models.CharField("Название голосования", max_length=255)
    description = models.TextField("Описание", blank=True)
    start_date = models.DateTimeField("Дата начала")
    end_date = models.DateTimeField("Дата окончания")
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Голосование"
        verbose_name_plural = "Голосования"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def clean(self):
        if self.start_date >= self.end_date:
            raise ValidationError("Дата начала должна быть раньше даты окончания")

    @property
    def is_active(self):
        return self.start_date <= now() <= self.end_date


class Nomination(models.Model):
    voting = models.ForeignKey(
        Voting,
        on_delete=models.CASCADE,
        related_name="nominations",
        verbose_name="Голосование"
    )
    title = models.CharField("Название номинации", max_length=255)
    description = models.TextField("Описание", blank=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Номинация"
        verbose_name_plural = "Номинации"
        unique_together = ("voting", "title")
        ordering = ["title"]

    def __str__(self):
        return f"{self.title} ({self.voting.title})"

    def votes_count(self):
        return sum(p.votes_count() for p in self.participants.all())
    votes_count.short_description = "Всего голосов"


class Participant(models.Model):
    nomination = models.ForeignKey(
        Nomination,
        on_delete=models.CASCADE,
        related_name="participants",
        verbose_name="Номинация"
    )
    name = models.CharField("Имя участника", max_length=255)
    description = models.TextField("Описание", blank=True)
    avatar = models.ImageField("Аватар", upload_to="participants/", blank=True, null=True)
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Участник"
        verbose_name_plural = "Участники"
        unique_together = ("nomination", "name")
        ordering = ["name"]

    def __str__(self):
        return self.name

    def votes_count(self):
        return self.votes.count()
    votes_count.short_description = "Количество голосов"


class Vote(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="votes",
        verbose_name="Пользователь"
    )
    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        related_name="votes",
        verbose_name="Участник"
    )
    voted_at = models.DateTimeField("Дата голосования", auto_now_add=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Голос"
        verbose_name_plural = "Голоса"
        unique_together = ("user", "participant")
        ordering = ["-voted_at"]

    def __str__(self):
        return f"{self.user} → {self.participant}"

    def clean(self):
        existing_vote = Vote.objects.filter(
            user=self.user,
            participant__nomination=self.participant.nomination
        ).exclude(pk=self.pk)
        if existing_vote.exists():
            raise ValidationError("Вы уже голосовали в этой номинации")
