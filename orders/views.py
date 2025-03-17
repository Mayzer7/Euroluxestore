from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Order, OrderItem
from carts.models import Cart
from .forms import OrderForm

@login_required
def create_order(request):
    cart_items = Cart.objects.filter(user=request.user)

    if not cart_items.exists():
        messages.error(request, "Корзина пуста!")
        return redirect('carts:cart_view')

    total_price = sum(item.total_price() for item in cart_items)

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.total_price = total_price
            if order.delivery_method == 'pickup':
                order.address = ''  # Убираем адрес, если самовывоз
            order.save()

            # Перенос товаров из корзины в OrderItem
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.sell_price(),  # Фиксируем цену товара
                )

            # Очищаем корзину пользователя
            cart_items.delete()

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
