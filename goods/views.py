from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.contrib import messages

from django.views.generic import TemplateView

from .models import Products, Categories, Review
from .forms import ReviewForm
from django.db.models import Avg


from django.db.models import Q, F, ExpressionWrapper, DecimalField

from .services.moderation import is_image_clean


class CatalogView(TemplateView):
    template_name = 'goods/catalog.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  
        context['title'] = 'EUROLUXE - Каталог'
        context['content'] = 'Магазин мебели EUROLUXE'

        # Получаем все товары с их средним рейтингом
        products_list = Products.objects.annotate(avg_rating=Avg('reviews__rating'))

        for product in products_list:
            product.avg_rating = round(product.avg_rating or 0)  # Округляем до целого числа

        # Обработка поиска
        search_query = self.request.GET.get('search', '')
        if search_query:
            products_list = products_list.filter(
                Q(name__icontains=search_query) | Q(description__icontains=search_query)
            )
            context['search_query'] = search_query  # Передаем запрос в контекст, чтобы отображать его в шаблоне

        # Фильтрация по категории
        category_slug = self.kwargs.get('category_slug') or self.request.GET.get('category')
        if category_slug and category_slug != 'all':
            category = get_object_or_404(Categories, slug=category_slug)
            products_list = products_list.filter(category=category)
            context['selected_category'] = category_slug

        # Фильтр по цене
        price_max = self.request.GET.get('price_max')
        if price_max:
            try:
                price_max = int(price_max)
                products_list = products_list.filter(price__lte=price_max)
            except ValueError:
                pass  

        # Фильтр по цвету
        selected_color = self.request.GET.get('color')
        if selected_color:
            products_list = products_list.filter(color=selected_color)
            context['selected_color'] = selected_color  

        # Фильтр по размерам
        width = self.request.GET.get('width')
        length = self.request.GET.get('length')
        height = self.request.GET.get('height')

        # Получаем все уникальные цвета
        colors = Products.objects.values('color').distinct().filter(color__isnull=False)

        # Определяем сортировку
        sort_order = self.request.GET.get('sort', '')

        if sort_order == 'discount':
            products_list = products_list.filter(discount__gt=0)
        elif sort_order == 'price_asc':
            products_list = products_list.annotate(
                final_price=ExpressionWrapper(
                    F('price') * (100 - F('discount')) / 100, 
                    output_field=DecimalField()
                )
            ).order_by('final_price')
        elif sort_order == 'price_desc':
            products_list = products_list.annotate(
                final_price=ExpressionWrapper(
                    F('price') * (100 - F('discount')) / 100, 
                    output_field=DecimalField()
                )
            ).order_by('-final_price')
        elif sort_order == 'rating_desc':
            products_list = products_list.order_by('-avg_rating')  # Сортировка по среднему рейтингу

        # Пагинация
        paginator = Paginator(products_list, 9)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Передаем данные в контекст
        context['products'] = page_obj
        context['page_obj'] = page_obj
        context['paginator'] = paginator
        context['colors'] = colors  
        context['categories'] = Categories.objects.all()
        context['products'] = products_list

        return context


class ProductDetailView(View):
    def get(self, request, product_slug):
        product = get_object_or_404(Products, slug=product_slug)
        reviews = Review.objects.filter(product=product).order_by('-created_at')
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0  # Средний рейтинг

        context = {
            'product': product,
            'title': f"{product.name}",
            'reviews': reviews,
            'avg_rating': round(avg_rating, 1),
            'review_form': ReviewForm(),
        }
        return render(request, 'goods/product.html', context)

    @method_decorator(login_required)
    def post(self, request, product_slug):
        product = get_object_or_404(Products, slug=product_slug)
        form = ReviewForm(request.POST, request.FILES)  # Не забываем про request.FILES

        # Если комментарий пустой или есть другая ошибка
        if 'comment' in form.errors:
            messages.error(request, "Поле с комментарием пустое")

        if form.is_valid():
            images = [form.cleaned_data.get(f'image_{i}') for i in range(1, 4)]
            
            for image in images:
                if image:
                    image.file.seek(0)  # на случай, если файл уже читался
                    if not is_image_clean(image.file, request.user.username):
                        messages.error(request, "Одно из загруженных изображений содержит запрещённый контент.")
                        return redirect('goods:product_detail', product_slug=product.slug)
            
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, "Ваш отзыв был добавлен!")
            return redirect('goods:product_detail', product_slug=product.slug)

        reviews = Review.objects.filter(product=product).order_by('-created_at')
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0

        context = {
            'product': product,
            'reviews': reviews,
            'avg_rating': round(avg_rating, 1),
            'review_form': form,
        }
        return render(request, 'goods/product.html', context)




# class ProductView(TemplateView):
#     template_name = 'goods/product.html'

#     products_list = Products.objects.all()

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)  
#         context['title'] = 'EUROLUXE - Товар'
#         context['content'] = 'Магазин мебели EUROLUXE'
#         return context

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


