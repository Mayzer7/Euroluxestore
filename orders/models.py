import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from goods.models import Products


class Order(models.Model):
    DELIVERY_CHOICES = [
        ('pickup', 'Самовывоз'),
        ('delivery', 'Доставка'),
    ]

    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('processing', 'В обработке'),
        ('shipped', 'Отправлен'),
        ('completed', 'Завершен'),
        ('canceled', 'Отменён'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Имя пользователя'
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Итоговая цена"
    )
    full_name = models.CharField(max_length=255, verbose_name="ФИО")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    delivery_method = models.CharField(
        max_length=10,
        choices=DELIVERY_CHOICES,
        verbose_name='Способ доставки'
    )
    address = models.TextField(blank=True, null=True, verbose_name="Адрес")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата оформления заказа")
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name='Статус заказа'
    )

    class Meta:
        db_table = 'Order'
        verbose_name = 'Заказ'
        verbose_name_plural = "Заказы"

    def clean(self):
        """Валидация: если выбран самовывоз, адрес должен быть пустым, а при доставке — обязательным."""
        if self.delivery_method == 'pickup' and self.address:
            raise ValidationError({'address': 'При самовывозе адрес не нужен.'})
        if self.delivery_method == 'delivery' and not self.address:
            raise ValidationError({'address': 'При доставке необходимо указать адрес.'})

    def total_items(self):
        """Считает общее количество товаров в заказе."""
        return self.items.aggregate(models.Sum('quantity'))['quantity__sum'] or 0
    total_items.short_description = "Всего товаров"

    def update_total_price(self):
        """Пересчитывает общую сумму заказа."""
        self.total_price = sum(item.total_price() for item in self.items.all())
        self.save()

    def __str__(self):
        return f"Заказ {self.id} ({self.get_status_display()}) от {self.full_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name='Заказ'
    )
    product = models.ForeignKey(
        Products,
        on_delete=models.CASCADE,
        verbose_name='Товар'
    )
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена за 1шт')
    

    class Meta:
        db_table = 'OrderItem'
        verbose_name = 'Заказанный товар'
        verbose_name_plural = "Заказанные товары"

    def total_price(self):
        """Возвращает итоговую цену позиции (цена * количество)."""
        if self.price is None or self.quantity is None:
            return 0  # Или можно вернуть None, если так логичнее
        return self.price * self.quantity
    
    def save(self, *args, **kwargs):
        """При изменении товара в заказе обновляем общую сумму заказа."""
        super().save(*args, **kwargs)
        self.order.update_total_price()

    def delete(self, *args, **kwargs):
        """При удалении товара из заказа обновляем сумму заказа."""
        super().delete(*args, **kwargs)
        self.order.update_total_price()

    def __str__(self):
        return f"{self.product.name} ({self.quantity} шт.)"
