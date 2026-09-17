from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.exceptions import ValidationError
from datetime import time, timedelta
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    notes = models.TextField(verbose_name='Что важно знать мастеру', blank=True)

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return f'Профиль для {self.user.username}'

class ProcedureType(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Тип процедуры')
    description = models.TextField(blank=True, verbose_name='Описание')

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


class WorkSettings(models.Model):
    work_starts = models.TimeField(default=time(10,0), verbose_name='Начало рабочего дня')
    work_ends = models.TimeField(default=time(18,0), verbose_name='Конец рабочего дня')
    lunch_starts = models.TimeField(null=True, blank=True, verbose_name='Начало обеда')
    lunch_ends = models.TimeField(null=True, blank=True, verbose_name='Конец обеда')
    min_hours_before_visit = models.PositiveSmallIntegerField(default=3, verbose_name='Минимум часов до визита')
    slot_step_minutes = models.PositiveSmallIntegerField(default=15, verbose_name='Шаг слота записи')
    monday = models.BooleanField(default=True, verbose_name='Понедельник')
    tuesday = models.BooleanField(default=True, verbose_name='Вторник')
    wednesday = models.BooleanField(default=True, verbose_name='Среда')
    thursday = models.BooleanField(default=True, verbose_name='Четверг')
    friday = models.BooleanField(default=True, verbose_name='Пятница')
    saturday = models.BooleanField(default=True, verbose_name='Суббота')
    sunday = models.BooleanField(default=True, verbose_name='Воскресенье')

    class Meta:
        verbose_name = 'Настройки рабочего времени'
        verbose_name_plural = 'Настройки рабочего времени'

    def __str__(self):
        return 'Настройки рабочего дня и записи'

    @classmethod
    def get_settings(cls):
        work_settings, _ = cls.objects.get_or_create(id=1)
        return work_settings

    def clean(self):
        if self.work_starts and self.work_ends:
            if self.work_starts >= self.work_ends:
                raise ValidationError({'work_ends': 'Конец рабочего дня должен быть позже начала'})

        if self.lunch_starts and not self.lunch_ends:
            raise ValidationError({'lunch_ends': 'Укажите конец обеда'})

        if self.lunch_ends and not self.lunch_starts:
            raise ValidationError({'lunch_starts': 'Укажите начало обеда'})

        if self.lunch_starts and self.lunch_ends:
            if self.lunch_starts >= self.lunch_ends:
                raise ValidationError({'lunch_ends': 'Конец обеда должен быть позже начала'})

            if self.lunch_starts < self.work_starts or self.lunch_ends > self.work_ends:
                raise ValidationError({'lunch_starts': 'Обед должен быть внутри рабочего дня'})


class TimeOff(models.Model):
    starts_at = models.DateTimeField(verbose_name='Начало нерабочего времени')
    ends_at = models.DateTimeField(verbose_name='Конец нерабочего времени')
    comment = models.CharField(max_length=100, blank=True, verbose_name='Комментарии')

    class Meta:
        verbose_name = 'Нерабочее время'
        verbose_name_plural = 'Нерабочее время'
        ordering = ['starts_at']

    def __str__(self):
        return f'Нерабочее время с {self.starts_at:%d.%m.%Y %H:%M} по {self.ends_at:%d.%m.%Y %H:%M}'

    def clean(self):
       
        if self.starts_at and self.ends_at:
            if self.starts_at >= self.ends_at:
                raise ValidationError('Окончание должно быть позже начала')

            booking_list = []
            for booking in Booking.objects.filter(status=Booking.Status.PLANNED, starts_at__lt=self.ends_at):
                booking_ends_at = booking.starts_at + timedelta(minutes=booking.total_duration_minutes)
                if booking_ends_at > self.starts_at:
                    booking_list.append(f'{booking.client} - {timezone.localtime(booking.starts_at):%d.%m %H:%M}')

            if booking_list:
                raise ValidationError(['В выбранном периоде есть запланированные записи:'] + booking_list)

            

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
        ordering = ['starts_at']

    def __str__(self):
        return f'{self.client} - {self.starts_at:%d.%m.%Y %H:%M}'

    def update_total(self):
        services = self.services.all()
        self.total_price = sum(s.price for s in services)
        self.total_duration_minutes = sum(s.duration_minutes for s in services)
        self.save(update_fields=['total_price', 'total_duration_minutes'])

    @classmethod
    def mark_finished(cls):
        now = timezone.now()

        for booking in cls.objects.filter(status=cls.Status.PLANNED, starts_at__lt=now):
            booking_ends_at = booking.starts_at + timedelta(minutes=booking.total_duration_minutes)

            if booking_ends_at < now:
                booking.status = cls.Status.DONE
                booking.save()

    
