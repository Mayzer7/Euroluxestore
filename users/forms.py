from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User

class UserRegistrationForm(UserCreationForm):
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    password1 = forms.CharField(widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

import re

class CustomUserChangeForm(UserChangeForm):
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Номер телефона'})
    )

    password1 = forms.CharField(
        label="Новый пароль",
        widget=forms.PasswordInput(attrs={'placeholder': 'Введите новый пароль'}),
        required=False
    )
    
    password2 = forms.CharField(
        label="Повторите пароль",
        widget=forms.PasswordInput(attrs={'placeholder': 'Повторите новый пароль'}),
        required=False
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'image']

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")

        if phone_number:
            # Разрешаем только цифры и + в начале
            if not re.match(r'^\+?\d{7,15}$', phone_number):
                raise ValidationError("Введите корректный номер телефона (7-15 цифр, можно с +).")

        return phone_number