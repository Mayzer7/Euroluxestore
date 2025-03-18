from django.conf import settings
from django.db import models
from goods.models import Products

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пользователь")

    class Meta:
        db_table = 'Cart'
        verbose_name = 'Корзина'
        verbose_name_plural = "Корзины"

    def total_price(self):
        return sum(item.total_price() for item in self.items.all())
    
    def __str__(self):
        return f"Корзина {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items", verbose_name="Корзина")
    product = models.ForeignKey(Products, on_delete=models.CASCADE, verbose_name="Товар")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")

    def total_price(self):
        return self.product.sell_price() * self.quantity
    
    def __str__(self):
        return f"{self.product.name} ({self.quantity})"

