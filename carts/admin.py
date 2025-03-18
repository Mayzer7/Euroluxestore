from django.contrib import admin
from .models import Cart, CartItem

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ("product", "quantity", "total_price_display")

    def total_price_display(self, obj):
        return obj.total_price()

    total_price_display.short_description = "Стоимость"

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "total_price_display")  # Убрали product и quantity
    search_fields = ("user__username",)
    ordering = ("user",)
    inlines = [CartItemInline]  # Вставляем товары в корзину

    def total_price_display(self, obj):
        return obj.total_price()

    total_price_display.short_description = "Общая стоимость"
