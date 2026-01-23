from import_export import resources, fields
from .models import Voting

class VotingResource(resources.ModelResource):
    
    # 1. Кастомизация: Метод get_export_queryset (Пункт 8 ТЗ)
    # Позволяет фильтровать данные перед выгрузкой.
    # Здесь мы выгружаем только те голосования, которые не являются пустыми (есть описание)
    def get_export_queryset(self, request, *args, **kwargs):
        return super().get_export_queryset(request, *args, **kwargs).exclude(title="")

    # 2. Кастомизация: Метод dehydrate_{field_name} (Пункт 8 ТЗ)
    # Изменяем отображение заголовка в Excel, добавляя статус
    def dehydrate_title(self, voting):
        status = "АКТИВНО" if voting.is_active else "ЗАВЕРШЕНО"
        return f"{voting.title} [{status}]"

    # 3. Кастомизация: Метод dehydrate_{field_name} (Пункт 8 ТЗ)
    # Форматируем дату создания для Excel в удобный вид
    def dehydrate_created_at(self, voting):
        if voting.created_at:
            return voting.created_at.strftime("%d.%m.%Y %H:%M")
        return ""

    class Meta:
        model = Voting
        # Указываем, какие поля мы хотим видеть в Excel-таблице
        fields = ('id', 'title', 'description', 'start_date', 'end_date', 'created_at')
        export_order = ('id', 'title', 'start_date', 'end_date', 'created_at', 'description')