from django.db import models

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