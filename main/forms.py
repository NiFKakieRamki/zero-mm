from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Booking
from django.utils import timezone
from datetime import timedelta

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['services', 'starts_at']


        widgets = {
            'services': forms.CheckboxSelectMultiple,
            'starts_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean(self):
        cleaned = super().clean()

        starts_at = cleaned.get('starts_at')
        services = cleaned.get('services')

        if starts_at and starts_at <= timezone.now():
            self.add_error('starts_at', 'Нельзя записаться на прошедшее время')

        if starts_at and services:
            total_minutes = 0
            for service in services:
                total_minutes += service.duration_minutes

            ends_at = starts_at + timedelta(minutes=total_minutes)

            same_day_booking = Booking.objects.filter(starts_at__date=starts_at.date(), status=Booking.Status.PLANNED)
            for booking in same_day_booking:
                booking_ends_at = booking.starts_at + timedelta(minutes=booking.total_duration_minutes)

                if starts_at < booking_ends_at and booking.starts_at < ends_at:
                    self.add_error('starts_at', 'Это время уже занято, выберите другое')
                    break


        return cleaned




class RegisterForm(UserCreationForm):

    phone = forms.CharField(max_length=20, label='Телефон')
    
    class Meta(UserCreationForm.Meta):
        fields = ('username', 'first_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['first_name'].required = True
        self.fields['email'].required = True




