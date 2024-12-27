from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView

from goods.models import Categories


class IndexView(TemplateView):
    template_name = 'main/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  
        context['title'] = 'EUROLUXE - Главная'
        context['content'] = 'Магазин мебели EUROLUXE'
        return context

# def index(request):

#     context = {
#         'title': 'Home - Главная',
#         'content': "Магазин мебели HOME",
#     }

#     return render(request, 'main/index.html', context)


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