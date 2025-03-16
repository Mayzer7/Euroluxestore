from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Cart
from goods.models import Products
from django.contrib import messages


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    quantity = int(request.GET.get('quantity', 1))

    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)

    if created:
        cart_item.quantity = quantity  # Устанавливаем количество, если объект только создаётся
    else:
        cart_item.quantity += quantity  # Увеличиваем количество, если товар уже в корзине
    
    cart_item.save()

    cart_count = Cart.objects.filter(user=request.user).count()

    messages.success(request, f'Товар {product.name} добавлен в корзину! ({quantity} шт.)')

    return JsonResponse({"cart_count": cart_count})

@login_required
def remove_from_cart(request, item_id):
    cart_item = Cart.objects.filter(id=item_id, user=request.user).first()
    
    if cart_item:
        cart_item.delete()
        messages.success(request, "Товар удалён из корзины.")
    else:
        messages.error(request, "Товар не найден в вашей корзине.")

    return redirect("carts:cart_view")

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Cart

@login_required
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.total_price() for item in cart_items)
    return render(request, "carts/cart.html", {"cart_items": cart_items, "total_price": total_price})

@login_required
def cart_count(request):
    cart_items_count = Cart.objects.filter(user=request.user).count()
    return JsonResponse({"cart_count": cart_items_count})