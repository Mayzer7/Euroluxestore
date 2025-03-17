from django.conf import settings
from django.db import models
from carts.models import Cart
from goods.models import Products

class Order(models.Model):
    DELIVERY_CHOICES = [
        ('pickup', 'Самовывоз'),
        ('delivery', 'Доставка'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Имя пользователя')
    cart = models.ManyToManyField(Cart)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Итоговая цена")
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    delivery_method = models.CharField(max_length=10, choices=DELIVERY_CHOICES, verbose_name='Способ доставки')
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата оформления заказа")

    class Meta:
        db_table = 'Order'
        verbose_name = 'Заказ'
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"Заказ {self.id} от {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items", verbose_name='Заказ')
    product = models.ForeignKey(Products, on_delete=models.CASCADE, verbose_name='Товар')
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')  # Фиксируем цену товара в момент покупки

    class Meta:
        db_table = 'OrderItem'
        verbose_name = 'Заказанный товар'
        verbose_name_plural = "Заказанные товары"

    def total_price(self):
        if self.price is None or self.quantity is None:
            return 0  # Или другое значение по умолчанию
        return self.price * self.quantity

    def __str__(self):
        return f"{self.product.name} ({self.quantity} шт.)"