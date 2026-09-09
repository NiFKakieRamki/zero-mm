from django import forms
from .models import Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['services', 'starts_at']

        widgets = {
            'services': forms.CheckboxSelectMultiple,
            'starts_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }