from django.conf import settings
from django.db import models
from goods.models import Products

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE, verbose_name="Товар")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.quantity})"

    def total_price(self):
        # Вызываем метод sell_price, а не обращаемся к нему как к атрибуту
        return self.product.sell_price() * self.quantity

