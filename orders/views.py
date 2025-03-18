from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Order, OrderItem
from carts.models import Cart, CartItem
from .forms import OrderForm

@login_required
def create_order(request):
    cart = Cart.objects.filter(user=request.user).first()

    if not cart or not cart.items.exists():
        messages.error(request, "Корзина пуста!")
        return redirect('carts:cart_view')

    cart_items = cart.items.all()
    total_price = cart.total_price()  # Используем метод total_price() из Cart

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            # Проверяем наличие всех товаров на складе
            for cart_item in cart_items:
                if cart_item.product.quantity < cart_item.quantity:
                    messages.error(
                        request,
                        f"Недостаточно товара: {cart_item.product.name}, всего товара на складе {cart_item.product.quantity}"
                    )
                    return redirect("carts:cart_view")

            # Создаём заказ
            order = form.save(commit=False)
            order.user = request.user
            order.total_price = total_price
            if order.delivery_method == 'pickup':
                order.address = ''  # Убираем адрес, если самовывоз
            order.save()

            # Переносим товары из корзины в OrderItem и уменьшаем количество в Products
            for cart_item in cart_items:
                product = cart_item.product
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=cart_item.quantity,
                    price=product.sell_price(),
                )
                product.quantity -= cart_item.quantity
                product.save()

            # Очищаем корзину
            cart.items.all().delete()

            messages.success(request, "Вы оформили заказ, дальнейшие указания придут на почту")
            return redirect('main:index')

    else:
        form = OrderForm(initial={
            'full_name': request.user.username,
            'email': request.user.email,
            'phone': request.user.phone_number,
        })

    return render(request, "orders/order_form.html", {
        "form": form,
        "cart_items": cart_items,
        "total_price": total_price
    })
