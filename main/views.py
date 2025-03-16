from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib import messages

import os
from django.conf import settings

from goods.models import Categories, Products, Review
from django.db.models import Avg

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

class IndexView(TemplateView):
    template_name = 'main/index.html'

    def post(self, request, *args, **kwargs):

        template_path = os.path.join(settings.BASE_DIR, 'users', 'templates', 'users', 'welcome_email.html')
        email = request.POST.get("email")
        print("Пользователь ввел email:", email)  # Вывод в консоль
        
        try:
            with open(template_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
        except FileNotFoundError:
            messages.error(request, "Шаблон письма не найден.")
            return self.get(request, *args, **kwargs)
        except Exception as ex:
            messages.error(request, f"Ошибка при чтении шаблона: {ex}")
            return self.get(request, *args, **kwargs)

        # Отправка письма
        if send_html_email([email], "Спасибо, что подписались на рассылку EUROLUXE", html_content):
            messages.success(request, 'Вам придёт письмо на почту')
        else:
            messages.error(request, "Ошибка при отправке письма.")

        return self.get(request, *args, **kwargs)
    


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        new_collection_products = Products.objects.filter(new_collection=True).annotate(avg_rating=Avg('reviews__rating'))
        top_sales_products = Products.objects.filter(top_sales=True).annotate(avg_rating=Avg('reviews__rating'))

        reviews = Review.objects.select_related('product', 'user').order_by('-created_at')[:10]  # Берем 10 свежих

        context['title'] = 'EUROLUXE - Главная'
        context['content'] = 'Магазин мебели EUROLUXE'
        context['new_collection_products'] = new_collection_products
        context['top_sales_products'] = top_sales_products
        context['reviews'] = reviews
        return context
    

def send_html_email(recipients_emails: list, subject: str, html_content: str) -> bool:
    login = os.getenv('YANDEX_EMAIL_LOGIN')
    password = os.getenv('YANDEX_EMAIL_PASSWORD')

    msg = MIMEMultipart('alternative')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = login
    msg['To'] = ', '.join(recipients_emails)

    msg.attach(MIMEText(html_content, 'html', 'utf-8'))

    try:
        with smtplib.SMTP_SSL('smtp.yandex.ru', 465, timeout=10) as s:
            s.login(login, password)
            s.sendmail(msg['From'], recipients_emails, msg.as_string())
            print("Email sent successfully!")
        return True
    except Exception as ex:
        print(f"An error occurred: {ex}")
        return False



class AboutView(TemplateView):
    template_name = 'main/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  
        context['title'] = 'EUROLUXE - О нас'
        context['content'] = 'Добро пожаловать в EUROLUXE – ваш проводник в мир премиальной мебели!'
        return context

class DeliveryView(TemplateView):
    template_name = 'main/delivery.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  
        context['title'] = 'EUROLUXE - Доставка'
        context['content'] = 'Доставка и оплата'
        context['text_on_page'] = 'Текст о том почему этот магазин такой крутой'
        return context
    
class ContactView(TemplateView):
    template_name = 'main/contact.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  
        context['title'] = 'EUROLUXE - Контакты'
        context['content'] = 'Контактная информация'
        return context

# def about(request):
#     context = {
#         'title': 'Home - О нас',
#         'content': "О нас",
#         'text_on_page': "Текст о том какой магазин крутой"
#     }

#     return render(request, 'main/about.html', context)