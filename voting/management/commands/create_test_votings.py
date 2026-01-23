from django.core.management.base import BaseCommand
from django.utils.timezone import now, timedelta
from voting.models import Voting


class Command(BaseCommand):
    help = "Создаёт тестовое голосование"

    def handle(self, *args, **kwargs):
        Voting.objects.create(
            title="Тестовое голосование",
            start_date=now(),
            end_date=now() + timedelta(days=5)
        )
        self.stdout.write(self.style.SUCCESS("Тестовое голосование создано"))
