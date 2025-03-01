from django import forms
from .models import Booking

class BookingForm(forms.ModelForm):
    expected_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Booking
        fields = ['expected_date']
