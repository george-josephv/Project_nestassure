from django import forms
from .models import Booking, User, Worker, Service

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
    first_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
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
            'dob': forms.DateInput(attrs={'type': 'date'}),
        }

class WorkerForm(forms.ModelForm):
    services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.all(),
        widget=forms.CheckboxSelectMultiple  # Allows selecting multiple services
    )

    class Meta:
        model = Worker
        fields = ['services']
