from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib import messages

from .forms import UserRegistrationForm
from django.contrib.auth.forms import AuthenticationForm

@login_required
def profile_view(request):
    return render(request, 'users/profile.html')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Вы успешно вошли!')
                return redirect('users:profile')
            else:
                messages.error(request, 'Неверные данные для входа.')
        else:
            messages.error(request, 'Неверные данные для входа.')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

def registration_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Авторизуем пользователя сразу после регистрации
            messages.success(request, 'Вы успешно зарегистрировались!')
            return redirect('users:profile')
        else:
            messages.error(request, 'Ошибка регистрации. Пожалуйста, попробуйте еще раз.')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/registration.html', {'form': form})