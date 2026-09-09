from django.db import models
from django.conf import settings

class ProcedureType(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Тип процедуры')

    class Meta:
        verbose_name = 'Тип процедуры'
        verbose_name_plural = 'Типы процедур'

    def __str__(self):
        return self.name

class Zone(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Зона')

    class Meta:
        verbose_name = 'Зона'
        verbose_name_plural = 'Зоны'

    def __str__(self):
        return self.name

class Service(models.Model):
    procedure_type = models.ForeignKey('ProcedureType', on_delete=models.PROTECT, verbose_name='Тип процедуры')
    zone = models.ForeignKey('Zone', on_delete=models.PROTECT, verbose_name='Зона')
    duration_minutes = models.PositiveSmallIntegerField(verbose_name='Продолжительность процедуры')
    price = models.DecimalField(max_digits=8, decimal_places=0, verbose_name='Цена')
    is_active = models.BooleanField(default=True, verbose_name='Статус')
    is_showcased = models.BooleanField(default=False, verbose_name='На витрине')

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'

    def __str__(self):
        return f'{self.procedure_type.name.upper()} - {self.zone} ( {self.duration_minutes} мин, {self.price} ₽ )'



class Booking(models.Model):

    class Status(models.TextChoices):
        PLANNED = 'planned', 'Запланирована'
        CANCELLED = 'cancelled', 'Отменена'
        DONE = 'done', 'Завершена'
        NO_SHOW = 'no_show', 'Не пришёл'

    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='booking', verbose_name='Клиент')
    services = models.ManyToManyField('Service', related_name='booking', verbose_name='Выбранные услуги')
    starts_at = models.DateTimeField(verbose_name='Начало визита')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLANNED, verbose_name='Статус')
    total_duration_minutes = models.PositiveSmallIntegerField(default=0, verbose_name='Длительность визита')
    total_price = models.DecimalField(max_digits=8, decimal_places=0, default=0, verbose_name='Стоимость визита')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создана')
    
    class Meta:
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'
        ordering = ['-starts_at']

    def __str__(self):
        return f'{self.client} - {self.starts_at:%d.%m.%Y %H:%M}'

    def update_total(self):
        services = self.services.all()
        self.total_price = sum(s.price for s in services)
        self.total_duration_minutes = sum(s.duration_minutes for s in services)
        self.save(update_fields=['total_price', 'total_duration_minutes'])
    
