# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=10, required=False, widget=forms.TextInput(attrs={'placeholder': 'Телефон'}))
    image = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'image', 'password1', 'password2']
