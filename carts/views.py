from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem
from goods.models import Products
from django.contrib import messages


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    quantity = int(request.GET.get('quantity', 1))

    # Получаем или создаем корзину пользователя
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Получаем или создаем товар в корзине
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if created:
        cart_item.quantity = quantity  # Если новый объект — задаём количество
    else:
        cart_item.quantity += quantity  # Если уже есть — увеличиваем количество

    cart_item.save()

    # Подсчитываем количество товаров в корзине (суммируем все количества)
    cart_count = sum(item.quantity for item in cart.items.all())

    messages.success(request, f'Товар {product.name} добавлен в корзину! ({quantity} шт.)')

    return JsonResponse({"cart_count": cart_count})

from django.urls import reverse

from django.urls import reverse

@login_required
def remove_from_cart(request, item_id):
    if request.method == "POST":
        item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        item.delete()

        messages.success(request, "Вы удалили товар из корзины.")
        return redirect("carts:cart_view")  # Перенаправляем пользователя обратно в корзину

    messages.error(request, "Ошибка удаления товара.")
    return redirect("carts:cart_view")




from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Cart

@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)  # Получаем корзину
    cart_items = cart.items.all()  # Берём все товары из `CartItem`
    total_price = sum(item.total_price() for item in cart_items)  

    return render(request, "carts/cart.html", {"cart_items": cart_items, "total_price": total_price})

from django.db.models import Sum

@login_required
def cart_count(request):
    cart_items_count = CartItem.objects.filter(cart__user=request.user).distinct().count()
    return JsonResponse({"cart_count": cart_items_count})


