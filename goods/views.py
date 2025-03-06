from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.contrib import messages

from django.views.generic import TemplateView

from .models import Products


from django.db.models import F, ExpressionWrapper, DecimalField


class CatalogView(TemplateView):
    template_name = 'goods/catalog.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  
        context['title'] = 'EUROLUXE - Каталог'
        context['content'] = 'Магазин мебели EUROLUXE'

        # Получаем все товары
        products_list = Products.objects.all()
        
        # Определяем сортировку
        sort_order = self.request.GET.get('sort', '')

        if sort_order == 'discount':
            # Фильтровать по товарам со скидкой
            products_list = products_list.filter(discount__gt=0)
        elif sort_order == 'price_asc':
            # Сортировка по цене с учётом скидочных товаров
            products_list = products_list.annotate(
                final_price=ExpressionWrapper(
                    F('price') * (100 - F('discount')) / 100, 
                    output_field=DecimalField()
                )
            ).order_by('final_price')
        elif sort_order == 'price_desc':
            # Сортировка по убыванию цены с учётом скидочных товаров
            products_list = products_list.annotate(
                final_price=ExpressionWrapper(
                    F('price') * (100 - F('discount')) / 100, 
                    output_field=DecimalField()
                )
            ).order_by('-final_price')
        
        # Пагинация
        paginator = Paginator(products_list, 9)  # 9 товаров на страницу
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['products'] = page_obj  # Передаем в шаблон объект страницы
        context['page_obj'] = page_obj  # Передаем объект страницы для пагинации
        context['paginator'] = paginator  # Передаем объект пагинатора для пагинации
        return context

class ProductView(TemplateView):
    template_name = 'goods/product.html'

    products_list = Products.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  
        context['title'] = 'EUROLUXE - Товар'
        context['content'] = 'Магазин мебели EUROLUXE'
        return context

# class CatalogView(ListView):
#     model = Products
#     template_name = "goods/catalog.html"
#     context_object_name = "goods"
#     paginate_by = 3

#     def get_queryset(self):
#         category_slug = self.kwargs.get("category_slug")
#         on_sale = self.request.GET.get('on_sale')
#         order_by = self.request.GET.get('order_by')
#         query = self.request.GET.get('q')

#         if category_slug == 'all':
#             goods = super().get_queryset()
#         elif query:
#             goods = q_search(query) 
#         else:
#             goods = super().get_queryset().filter(category__slug=category_slug)
#             if not goods.exists():
#                 raise Http404()

#         if on_sale:
#             goods = goods.filter(discount__gt=0)
        
#         if order_by and order_by != "default":
#             goods = goods.order_by(order_by)

#         return goods

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['title'] = "EUROLUXE - Каталог"
#         context['slug_url'] = self.kwargs.get("category_slug")
#         return context


# class ProductView(DetailView):
#     template_name = "goods/product.html"
#     slug_url_kwarg = "product_slug"
#     context_object_name = "product"
#     model = Products

#     def get_object(self, queryset=None):
#         return get_object_or_404(Products, slug=self.kwargs.get(self.slug_url_kwarg))

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['title'] = self.object.name
#         context['reviews'] = self.object.reviews.all()
#         context['form'] = ReviewForm()
#         return context

#     @method_decorator(login_required)
#     def post(self, request, *args, **kwargs):
#         self.object = self.get_object()
        
#         # Проверяем, удаление это или добавление
#         if 'delete_review' in request.POST:
#             review_id = request.POST.get('review_id')
#             review = get_object_or_404(Review, id=review_id, user=request.user)
#             review.delete()
#             messages.success(request, "Отзыв успешно удалён.")
#             return redirect('goods:product_detail', product_slug=self.object.slug)

#         # Добавление отзыва
#         form = ReviewForm(request.POST, request.FILES)
#         if form.is_valid():
#             review = form.save(commit=False)
#             review.product = self.object
#             review.user = request.user
#             review.save()
#             messages.success(request, "Отзыв успешно добавлен.")
#             return redirect('goods:product_detail', product_slug=self.object.slug)
        
#         context = self.get_context_data()
#         context['form'] = form
#         return self.render_to_response(context)


# def catalog(request, category_slug = None):

    # page = request.GET.get('page', 1)
    # on_sale = request.GET.get('on_sale', None)
    # order_by = request.GET.get('order_by', None)
    # query = request.GET.get('q', None)

    # if category_slug == 'all':
    #     goods = Products.objects.all()
    # elif query:
    #     goods = q_search(query) 
    # else:
    #     goods = Products.objects.filter(category__slug=category_slug)
    #     if not goods.exists():
    #         raise Http404()


    # if on_sale:
    #     goods = goods.filter(discount__gt=0)
        
    # if order_by and order_by != "default":
    #     goods = goods.order_by(order_by)
    
#     paginator = Paginator(goods, 3)
#     current_page = paginator.page(int(page))

#     context = {
#         'title': 'Home - Каталог',
#         'goods': current_page,
#         'slug_url': category_slug
#     }
#     return render(request, 'goods/catalog.html', context)



# def product(request, product_slug):
    
#     product = Products.objects.get(slug=product_slug)

#     context = {
#         'product': product
#     }

#     return render(request, 'goods/product.html', context)


