from django.contrib import admin
from django.utils.html import format_html

# Register your models here.

from goods.models import Categories, Products, Review

# admin.site.register(Categories) - нельзя внести изменения в админку, поэтому плохой способ регистрации
# admin.site.register(Products) - ниже прописан более гибкий способ

@admin.register(Categories)
class CategoriesAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ['name',]
    
@admin.register(Products)
class ProductsAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ['name', 'quantity', 'price', 'discount']
    list_editable = ['discount',]
    search_fields = ['name', 'description']
    list_filter = ['discount', 'quantity', 'category', 'new_collection', 'top_sales']
    fields = [
        "name",
        "category",
        "slug",
        "description",
        ("image", "image_additional_1", "image_additional_2", "image_additional_3"),
        ("price", "discount"),
        "color",
        ("width", "length", "height"),
        "quantity",
        "new_collection",
        "top_sales",
    ]



@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'created_at', 'comment_preview', 'images_preview']
    list_filter = ['product', 'user', 'rating', 'created_at']
    search_fields = ['user__username', 'product__name', 'comment']
    date_hierarchy = 'created_at'
    list_per_page = 20

    # Функция для предварительного просмотра комментария
    def comment_preview(self, obj):
        return obj.comment[:50] + '...' if obj.comment else 'Нет комментария'
    comment_preview.short_description = 'Комментарий'

    # Функция для отображения изображений в админке
    def images_preview(self, obj):
        images = []
        if obj.image_1:
            images.append(format_html('<img src="{}" width="50" height="50" />', obj.image_1.url))
        if obj.image_2:
            images.append(format_html('<img src="{}" width="50" height="50" />', obj.image_2.url))
        if obj.image_3:
            images.append(format_html('<img src="{}" width="50" height="50" />', obj.image_3.url))
        return format_html(' '.join(images))
    images_preview.short_description = 'Изображения'

    # Функция для отображения средней оценки
    def average_rating(self, obj):
        avg_rating = obj.product.average_rating()
        return f'{avg_rating}/5'
    average_rating.short_description = 'Средняя оценка'