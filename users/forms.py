from django import forms
from django.contrib.auth.forms import AuthenticationForm

from users.models import User

class UserLoginForm(AuthenticationForm):
    class Meta:
        model = User
        field = ['username', 'surname']

    username = forms.CharField()
    password = forms.CharField()

    # username = forms.CharField(
    #     label = 'Имя пользователя',
    #     widget=forms.TextInput(attrs={"autofocus": True,
    #                                   'class': 'form-control',
    #                                   'placeholder': 'Введите имя пользователя'})
    # )
    # password = forms.CharField(
    #     label = 'Пароль',
    #     widget=forms.PasswordInput(attrs={"autocomplete": "current-password",
    #                                       'class': 'form-control',
    #                                       'placeholder': 'Введите ваш пароль'})
    # )
