import smtplib

from django.conf import settings
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.hashers import make_password
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.db.models import Prefetch
from django.views.generic import CreateView, UpdateView, TemplateView
from django.views.generic import FormView

from django.template.loader import render_to_string  # Для рендера HTML из шаблона

from django.core.cache import cache

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

from users.models import User 
from users.forms import UserLoginForm, UserRegistrationForm, UserPasswordResetForm, PasswordResetConfirmForm ,ProfileForm
from common.mixins import CacheMixin
from django.urls import reverse, reverse_lazy
from carts.models import Cart
from orders.models import Order, OrderItem



class UserLoginView(LoginView):
    template_name = 'users/login.html'
    form_class = UserLoginForm
    # success_url = reverse_lazy('main:index')

    def get_success_url(self):
        redirect_page = self.request.POST.get('next', None)
        if redirect_page and redirect_page != reverse('user:logout'):
            return redirect_page
        return reverse_lazy('main:index')

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['title'] = 'EUROLUXE - Авторизация'
        return context    
    
    def form_valid(self, form):
        session_key = self.request.session.session_key

        user = form.get_user()

        if user:
            auth.login(self.request, user)
            if session_key:
                # delete old authorized user carts
                forgot_carts = Cart.objects.filter(user=user)
                if forgot_carts.exists():
                    forgot_carts.delete()
                # add new authorized user carts from anonimous session
                Cart.objects.filter(session_key=session_key).update(user=user)

                messages.success(self.request, f"{user.username}, Вы вошли в аккаунт")

                return HttpResponseRedirect(self.get_success_url())     



class UserRegistationView(CreateView):
    template_name = 'users/registration.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('users:profile')

    def form_valid(self, form):
        session_key = self.request.session.session_key
        user = form.save()

        # Указываем backend для аутентификации
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        auth.login(self.request, user)

        if session_key:
            Cart.objects.filter(session_key=session_key).update(user=user)

        messages.success(self.request, f"{user.username}, Вы успешно зарегистрированы и вошли в аккаунт")

        return HttpResponseRedirect(self.success_url)
    

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['title'] = 'EUROLUXE - Регистрация'
        return context    



class UserPasswordResetView(FormView):
    template_name = 'users/password_reset.html'
    form_class = UserPasswordResetForm  # Используем форму с проверкой только email
    success_url = reverse_lazy('main:index')  # Сюда перекидывает после успешного ввода

    def form_valid(self, form):
        email = form.cleaned_data.get('email')

        try:
            # Проверяем, есть ли пользователь с этим email
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Если пользователь не найден, возвращаем форму с ошибкой
            form.add_error('email', 'Пользователь с таким email не найден.')
            return self.form_invalid(form)
        
        # Генерация токена и ссылки
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
    
        reset_url = self.request.build_absolute_uri(
            reverse('users:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        )

        # Генерация HTML-письма с помощью шаблона
        try:
            html_content = render_to_string('users/email_password_reset.html', {
                'user': user,
                'reset_url': reset_url
            })
            self.send_html_email(
                recipients_emails=[email],
                subject='Восстановление пароля в EUROLUXE-STORE',
                html_content=html_content
            )
            
            messages.success(self.request, "На вашу почту направлено письмо с восстановлением!")

        except Exception as ex:
            messages.error(self.request, f"Не удалось отправить письмо: {ex}")
            return self.form_invalid(form)

        # Если пользователь найден и письмо успешно отправлено, редиректим на success_url
        return super().form_valid(form)
    
    def send_html_email(self, recipients_emails: list, subject: str, html_content: str):
        """Функция отправки HTML-писем."""
        login = settings.YANDEX_EMAIL
        password = settings.YANDEX_PASSWORD  # Используем пароль из настроек

        # Создание сообщения
        msg = MIMEMultipart('alternative')
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = login
        msg['To'] = ', '.join(recipients_emails)

        # Добавляем HTML-контент
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))

        try:
            # Для SSL используйте порт 465
            with smtplib.SMTP_SSL('smtp.yandex.ru', 465, timeout=10) as s:
                s.login(login, password)
                s.sendmail(msg['From'], recipients_emails, msg.as_string())
        except Exception as ex:
            raise Exception(f"Ошибка отправки письма: {ex}")


    def form_invalid(self, form):
        # Форма останется на той же странице с ошибками
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'EUROLUXE - Забыли пароль'
        return context


class PasswordResetConfirmView(FormView):
    template_name = 'users/password_reset_confirm.html'
    form_class = PasswordResetConfirmForm  # Форма для ввода нового пароля
    success_url = reverse_lazy('main:index')

    def form_valid(self, form):
        uidb64 = self.kwargs.get('uidb64')
        token = self.kwargs.get('token')

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            messages.error(self.request, "Некорректная ссылка для сброса пароля.")
            return self.form_invalid(form)

        token_generator = PasswordResetTokenGenerator()
        if not token_generator.check_token(user, token):
            messages.error(self.request, "Ссылка для сброса пароля недействительна.")
            return self.form_invalid(form)

        # Обновление пароля
        new_password = form.cleaned_data.get('new_password1')
        user.password = make_password(new_password)
        user.save()

        messages.success(self.request, "Пароль успешно обновлен!")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем пользователя из uidb64 и добавляем в контекст
        uidb64 = self.kwargs.get('uidb64')
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            context['username'] = user.username  # Добавляем имя пользователя
        except (User.DoesNotExist, ValueError, TypeError):
            context['username'] = ''  # Если пользователь не найден, оставляем пустым

        context['uidb64'] = uidb64
        context['token'] = self.kwargs.get('token')
        context['title'] = 'EUROLUXE - Сброс пароля'
        return context


# LoginRequiredMixin позволяет проверить зарегистрирован ли пользователь
class UserProfileView(LoginRequiredMixin,CacheMixin, UpdateView):
    template_name = 'users/profile.html'
    form_class = ProfileForm
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset = None):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, "Профайл успешно обновлён")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, "Произошла ошибка")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'EUROLUXE - Кабинет'

    
        orders = Order.objects.filter(user=self.request.user).prefetch_related(
            Prefetch(
                "orderitem_set",
                queryset=OrderItem.objects.select_related("product")
            )
        ).order_by("-id")
        
        context['orders'] = self.set_get_cache(orders, f"user_{self.request.user.id}_orders", 60 * 2)
        return context

class UserCartView(TemplateView):
    template_name = 'users/users_cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'EUROLUXE - Корзина' 
        return context


@login_required
def logout(request):
    messages.success(request, f"{request.user.username}, Вы вышли из аккаунта")
    auth.logout(request)
    return redirect(reverse('main:index'))




# def login(request):
#     if request.method == 'POST':
#         form = UserLoginForm(data=request.POST)
#         if form.is_valid():
#             username = request.POST['username']
#             password = request.POST['password']
#             user = auth.authenticate(username=username, password=password)

#             session_key = request.session.session_key

#             if user:
#                 auth.login(request, user)
#                 messages.success(request, f"{username}, Вы вошли в аккаунт")

#                 if session_key:
#                     # delete old authorized user carts
#                     forgot_carts = Cart.objects.filter(user=user)
#                     if forgot_carts.exists():
#                         forgot_carts.delete()
#                     # add new authorized user carts from anonimous session
#                     Cart.objects.filter(session_key=session_key).update(user=user)

#                 redirect_page = request.POST.get('next', None)
#                 if redirect_page and redirect_page != reverse('user:logout'):
#                     return HttpResponseRedirect(request.POST.get('next'))
            
#                 return HttpResponseRedirect(reverse('user:profile'))
#     else:
#         form = UserLoginForm()

#     context = {
#         'title': 'Home - Авторизация',
#         'form': form
#     }
#     return render(request, 'users/login.html', context)


# def registration(request):
#     if request.method == 'POST':
#         form = UserRegistrationForm(data=request.POST)
#         if form.is_valid():
#             form.save()

#             session_key = request.session.session_key

#             user = form.instance
#             auth.login(request, user)

#             if session_key:
#                 Cart.objects.filter(session_key=session_key).update(user=user)

#             messages.success(request, f"{user.username}, Вы успешно зарегистрированы и вошли в аккаунт")
#             return HttpResponseRedirect(reverse('main:index'))
#     else:
#         form = UserRegistrationForm()
    
#     context = {
#         'title': 'Home - Регистрация',
#         'form': form
#     }
#     return render(request, 'users/registration.html', context)



# @login_required
# def profile(request):
#     if request.method == 'POST':
#         form = ProfileForm(data=request.POST, instance=request.user, files=request.FILES)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Профайл успешно обновлён")
#             return HttpResponseRedirect(reverse('user:profile'))
#     else:
#         form = ProfileForm(instance=request.user)

#     orders = (
    #     Order.objects.filter(user=request.user).prefetch_related(
    #         Prefetch(
    #             "orderitem_set",
    #             queryset=OrderItem.objects.select_related("product")
    #         )
    #     ).order_by("-id")
    # )

#     context = {
#         'title': 'Home - Кабинет',
#         'form': form,
#         'orders': orders,
#     }
#     return render(request, 'users/profile.html', context)


# def users_cart(request):
# return render(request, 'users/users_cart.html')
