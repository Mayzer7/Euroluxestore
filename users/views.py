from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout ,authenticate
from django.contrib import messages

from .forms import UserRegistrationForm, CustomUserChangeForm
from django.contrib.auth.forms import AuthenticationForm

from django.contrib.auth.forms import UserChangeForm
from carts.models import Cart, CartItem
from orders.models import Order
from users.models import User
from goods.models import Products

from django.urls import reverse_lazy

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView
from django.contrib.auth import update_session_auth_hash


from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = CustomUserChangeForm
    template_name = 'users/profile.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        cart, created = Cart.objects.get_or_create(user=self.request.user)
        cart_items = cart.items.all()  # Все товары из корзины пользователя
        total_price = sum(item.total_price() for item in cart_items)  

        context['title'] = 'EUROLUXE - Личный кабинет'
        context['content'] = 'Магазин мебели EUROLUXE'
        context['cart_items'] = cart_items
        context['total_price'] = total_price
        context['orders'] = Order.objects.filter(user=self.request.user).prefetch_related('items__product')

        return context

    def form_valid(self, form):
        password1 = form.cleaned_data.get("password1")
        password2 = form.cleaned_data.get("password2")

        if password1 and password2:
            if password1 != password2:
                messages.error(self.request, "Пароли не совпадают!")
                return self.form_invalid(form)  # Не сохраняем изменения

            try:
                validate_password(password1)
            except ValidationError as e:
                for error in e.messages:
                    form.add_error("password1", error)
                return self.form_invalid(form)  # Не сохраняем

            self.object.set_password(password1)
            update_session_auth_hash(self.request, self.object)

        messages.success(self.request, "Данные успешно сохранены!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Ошибка при сохранении данных.")
        return super().form_invalid(form)


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
