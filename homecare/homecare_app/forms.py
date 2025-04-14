
from django import forms
from django.core.exceptions import ValidationError
from .models import Booking, User, Worker, Service
import re

BLOOD_GROUP_CHOICES = [
    ('A+', 'A+'),
    ('A-', 'A-'),
    ('B+', 'B+'),
    ('B-', 'B-'),
    ('O+', 'O+'),
    ('O-', 'O-'),
    ('AB+', 'AB+'),
    ('AB-', 'AB-'),
]

DISTRICT_CHOICES = [
    ("Thiruvananthapuram", "Thiruvananthapuram"),
    ("Kollam", "Kollam"),
    ("Pathanamthitta", "Pathanamthitta"),
    ("Alappuzha", "Alappuzha"),
    ("Kottayam", "Kottayam"),
    ("Idukki", "Idukki"),
    ("Ernakulam", "Ernakulam"),
    ("Thrissur", "Thrissur"),
    ("Palakkad", "Palakkad"),
    ("Malappuram", "Malappuram"),
    ("Kozhikode", "Kozhikode"),
    ("Wayanad", "Wayanad"),
    ("Kannur", "Kannur"),
    ("Kasaragod", "Kasaragod"),
]

STATE_CHOICES = [
    ("Kerala", "Kerala")
]

class BookingForm(forms.ModelForm):
    expected_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Booking
        fields = ['expected_date']


class EditProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30, required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30, required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    blood_group = forms.ChoiceField(
        choices=BLOOD_GROUP_CHOICES, 
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    district = forms.ChoiceField(
        choices=DISTRICT_CHOICES, 
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    state = forms.ChoiceField(
        choices=STATE_CHOICES, 
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'dob', 'state', 'district', 'place', 'housename', 'profile_picture', 'blood_group', 'first_name', 'last_name']
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if " " in username:
            raise ValidationError("Username must not contain spaces.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            raise ValidationError("Enter a valid email address.")
        return email

    def clean_phone_number(self):
        phone = self.cleaned_data.get("phone_number")
        if not re.match(r'^\d{10}$', phone):
            raise ValidationError("Phone number must be exactly 10 digits.")
        return phone


class WorkerForm(forms.ModelForm):
    services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.all(),
        widget=forms.CheckboxSelectMultiple  # Allows selecting multiple services
    )

    class Meta:
        model = Worker
        fields = ['services']
