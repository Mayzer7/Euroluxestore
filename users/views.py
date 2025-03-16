from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout ,authenticate
from django.contrib import messages

from .forms import UserRegistrationForm, CustomUserChangeForm
from django.contrib.auth.forms import AuthenticationForm

from django.contrib.auth.forms import UserChangeForm
from carts.models import Cart

@login_required
def profile_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.total_price() for item in cart_items)

    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)

        if form.is_valid():
            form.save()
            messages.success(request, 'Данные успешно сохранены!')
            return redirect('users:profile')
        else:
            messages.error(request, 'Ошибка при сохранении данных.')
    else:
        form = CustomUserChangeForm(instance=request.user)

    return render(request, 'users/profile.html', {
        'form': form,
        'cart_items': cart_items,
        'total_price': total_price
    })

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)  # Входим в систему
                messages.success(request, 'Вы успешно вошли!')
                return redirect('main:index')  # Редирект на главную страницу
            else:
                messages.error(request, 'Неверные данные для входа.')
        else:
            messages.error(request, 'Неверные данные для входа.')
    else:
        form = AuthenticationForm()

    return render(request, 'users/login.html', {'form': form})

def registration_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Создаём объект, но не сохраняем
            user.save()  # Сохраняем в базу данных
            messages.success(request, 'Вы успешно зарегистрировались!')
            return redirect('users:login')
        else:
            print(form.errors)  # Выведет ошибки в консоль
            messages.error(request, 'Ошибка регистрации. Проверьте введённые данные.')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/registration.html', {'form': form})


def logout_view(request):
    """Выход из аккаунта"""
    logout(request)
    messages.success(request, 'Вы успешно вышли из аккаунта!')
    return redirect('main:index')  # Перенаправляем на страницу логина (или другую страницу)
