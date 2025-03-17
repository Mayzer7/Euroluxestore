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

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 or password2:
            if password1 != password2:
                self.add_error("password2", "Пароли не совпадают")

        return cleaned_data