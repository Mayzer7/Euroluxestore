from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):  # Или admin.StackedInline для другого вида
    model = OrderItem
    extra = 0  # Чтобы не добавлялись пустые поля
    readonly_fields = ('product', 'quantity', 'price', 'total_price')

    def total_price(self, obj):
        return obj.total_price()
    total_price.short_description = "Сумма"

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'delivery_method', 'created_at')
    list_filter = ('user', 'created_at', 'delivery_method')
    search_fields = ('user__username', 'email', 'phone')
    inlines = [OrderItemInline]  # Встраиваем товары в заказ

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price', 'total_price')
    list_filter = ('order__user',)
    search_fields = ('product__name', 'order__user__username')

    def total_price(self, obj):
        return obj.total_price()
    total_price.short_description = "Сумма"
