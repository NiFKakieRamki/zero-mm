from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['services', 'starts_at']

        widgets = {
            'services': forms.CheckboxSelectMultiple,
            'starts_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class RegisterForm(UserCreationForm):

    phone = forms.CharField(max_length=20, label='Телефон')
    
    class Meta(UserCreationForm.Meta):
        fields = ('username', 'first_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['first_name'].required = True
        self.fields['email'].required = True




