from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem
from goods.models import Products
from django.contrib import messages


def add_to_cart(request, product_id):
    if not request.user.is_authenticated:
        messages.error(request, "Чтобы добавить товар в корзину, войдите в аккаунт.")
        return JsonResponse({"success": False, "redirect": "/user/login/"})  # Вернем JSON с редиректом

    product = get_object_or_404(Products, id=product_id)
    quantity = int(request.GET.get('quantity', 1))

    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if created:
        cart_item.quantity = quantity
    else:
        cart_item.quantity += quantity

    cart_item.save()
    messages.success(request, "Вы успешно добавили товар в корзину.")

    cart_count = sum(item.quantity for item in cart.items.all())
    return JsonResponse({"cart_count": cart_count, "success": True})

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

def cart_view(request):
    # Если пользователь не авторизован
    if not request.user.is_authenticated:
        messages.error(request, "Чтобы посмотреть корзину войдите в аккаунт")
        return redirect('users:login')  # или redirect('your_login_url_name')

    cart, created = Cart.objects.get_or_create(user=request.user)  # Получаем корзину
    cart_items = cart.items.all()  # Берём все товары из `CartItem`
    total_price = sum(item.total_price() for item in cart_items)

    return render(request, "carts/cart.html", {"cart_items": cart_items, "total_price": total_price})


from django.db.models import Sum

@login_required
def cart_count(request):
    cart_items_count = CartItem.objects.filter(cart__user=request.user).distinct().count()
    return JsonResponse({"cart_count": cart_items_count})


