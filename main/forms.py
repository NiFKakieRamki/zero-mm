from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Booking, WorkSettings, TimeOff
from django.utils import timezone
from datetime import timedelta, datetime

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['services', 'starts_at']


        widgets = {
            'services': forms.CheckboxSelectMultiple,
        }

    def clean(self):
        cleaned = super().clean()
        work_settings = WorkSettings.get_settings()

        starts_at = cleaned.get('starts_at')
        services = cleaned.get('services')
        working_days = [work_settings.monday, work_settings.tuesday, work_settings.wednesday, work_settings.thursday, work_settings.friday, work_settings.saturday, work_settings.sunday]
        time_booking = timezone.now() + timedelta(hours=work_settings.min_hours_before_visit)

        if starts_at and not working_days[starts_at.weekday()]:
            self.add_error('starts_at', 'Вы выбрали нерабочий день')

        if starts_at and starts_at <= time_booking:
            self.add_error('starts_at', f'Ближайшее время для записи — через {work_settings.min_hours_before_visit} ч.')

        if starts_at and starts_at.time() < work_settings.work_starts:
            self.add_error('starts_at', f'Начало рабочего дня: {work_settings.work_starts:%H:%M} (по мск)')

        if starts_at and services:
            total_minutes = 0
            for service in services:
                total_minutes += service.duration_minutes

            ends_at = starts_at + timedelta(minutes=total_minutes)

            if work_settings.lunch_starts and work_settings.lunch_ends:
                lunch_start = timezone.make_aware(datetime.combine(starts_at.date(), work_settings.lunch_starts))
                lunch_end = timezone.make_aware(datetime.combine(starts_at.date(), work_settings.lunch_ends))

                if starts_at < lunch_end and ends_at > lunch_start:
                    self.add_error('starts_at', 'Это время попадает на перерыв, выберите другое')

            for time_off in TimeOff.objects.all():
                if starts_at < time_off.ends_at and ends_at > time_off.starts_at:
                    self.add_error('starts_at', 'Мастер не работает в это время. Выберите другое')
                    break

            if ends_at.time() > work_settings.work_ends:
                self.add_error('starts_at', f'Визит заканчивается позже рабочего времени (Работаем с {work_settings.work_starts:%H:%M} до {work_settings.work_ends:%H:%M})')

            same_day_booking = Booking.objects.filter(starts_at__date=starts_at.date(), status=Booking.Status.PLANNED)
            for booking in same_day_booking:
                booking_ends_at = booking.starts_at + timedelta(minutes=booking.total_duration_minutes)

                if starts_at < booking_ends_at and ends_at > booking.starts_at:
                    self.add_error('starts_at', 'Это время уже занято, выберите другое')
                    break


        return cleaned


class RegisterForm(UserCreationForm):

    phone = forms.CharField(max_length=20, label='Телефон')
    consent = forms.BooleanField(required=True, label='Даю согласие на обработку персональных данных')
    
    class Meta(UserCreationForm.Meta):
        fields = ('username', 'first_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['first_name'].required = True
        self.fields['email'].required = True
        self.fields['email'].label = 'Электронная почта'

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Эта почта уже используется')
        return email


class ProfileForm(forms.ModelForm):
    phone = forms.CharField(max_length=20, label='Телефон')
    notes = forms.CharField(label='Что важно знать мастеру', required=False, widget=forms.Textarea)

    class Meta:
        model = User
        fields = ('first_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['email'].required = True
        self.fields['first_name'].label = 'Имя'
        self.fields['email'].label = 'Электронная почта'

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exclude(id=self.instance.id).exists():
            raise forms.ValidationError('Эта почта уже используется')
        return email



