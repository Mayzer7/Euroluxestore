from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import UserChangeForm
from .models import User

class UserRegistrationForm(UserCreationForm):
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    password1 = forms.CharField(widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')



class CustomUserChangeForm(UserChangeForm):
    phone_number = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'placeholder': 'Номер телефона'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'image']  # Все поля, которые вы хотите изменить