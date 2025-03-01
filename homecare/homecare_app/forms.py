from django import forms
from .models import Booking, User

class BookingForm(forms.ModelForm):
    expected_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Booking
        fields = ['expected_date']
class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'dob', 'state', 'district', 'place', 'housename', 'profile_picture']
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
        }