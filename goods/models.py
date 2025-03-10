import os
from django.conf import settings
from django.db import models
from django.urls import reverse
from users.models import User

from django.db.models import Avg

# Create your models here.

class Categories(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name='Название')
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True, verbose_name='URL')

    class Meta:
        db_table = 'category'
        verbose_name = 'Категорию'
        verbose_name_plural = "Категории"
        ordering = ("id", )

    def __str__(self) -> str:
        return self.name


class Products(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name='Название')
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True, verbose_name='URL')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    image = models.ImageField(upload_to='goods_images', blank=True, null=True, verbose_name='ОСНОВНОЕ ИЗОБРАЖЕНИЕ')

    image_additional_1 = models.ImageField(upload_to='goods_images', blank=True, null=True, verbose_name='ДОПОЛНИТЕЛЬНОЕ ИЗОБРАЖЕНИЕ')
    image_additional_2 = models.ImageField(upload_to='goods_images', blank=True, null=True, verbose_name='ДОПОЛНИТЕЛЬНОЕ ИЗОБРАЖЕНИЕ')
    image_additional_3 = models.ImageField(upload_to='goods_images', blank=True, null=True, verbose_name='ДОПОЛНИТЕЛЬНОЕ ИЗОБРАЖЕНИЕ')

    price = models.DecimalField(default=0.00, max_digits=7, decimal_places=2, verbose_name="Цена")

    color = models.CharField(max_length=150, unique=True, blank=True, null=True, verbose_name='Цвет')

    width = models.PositiveIntegerField(unique=True, blank=True, null=True, verbose_name='Ширина (см)')
    length = models.PositiveIntegerField(unique=True, blank=True, null=True, verbose_name='Длина (см)')
    height = models.PositiveIntegerField(unique=True, blank=True, null=True, verbose_name='Высота (см)')

    discount = models.DecimalField(default=0.00, max_digits=4, decimal_places=2, verbose_name="Скидка в %")
    quantity = models.PositiveIntegerField(default=0, verbose_name='Количество')
    category = models.ForeignKey(to=Categories, on_delete=models.CASCADE, verbose_name='Категория')
    
    class Meta:
        db_table = 'product'
        verbose_name = 'Продукт'
        verbose_name_plural = "Продукты"
        ordering = ("id", )    

    def __str__(self) -> str:
        return f"{self.name} Количество - {self.quantity}"
    
    def get_absolute_url(self):
        return reverse("catalog:product", kwargs={"product_slug": self.slug})
    
    def display_id(self):
        return f"{self.id:05}" 
    
    def sell_price(self):
        if self.discount:
            return int(self.price * ((100 - self.discount) / 100))
        return int(self.price)
    
    def average_rating(self):
        avg_rating = self.reviews.aggregate(Avg('rating'))['rating__avg']
        return round(avg_rating, 1) if avg_rating else 0
    





class Review(models.Model):
    product = models.ForeignKey('Products', on_delete=models.CASCADE, related_name='reviews', verbose_name="Продукт")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    rating = models.PositiveIntegerField(default=5, verbose_name="Оценка")
    comment = models.TextField(blank=True, null=True, verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        db_table = 'review'
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Отзыв от {self.user.username} на {self.product.name} ({self.rating}/5)"