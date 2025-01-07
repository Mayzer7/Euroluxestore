from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

from orders.models import Order, OrderItem

# Register your models here.

# admin.site.register(Order)
# admin.site.register(OrderItem) 

class OrderItemTabulareAdmin(admin.TabularInline):
    model = OrderItem
    fields = "product", "name", "price", "quantity"
    search_fields = (
        "product",
        "name",
    )
    extra = 0

@admin.register(OrderItem)
class OrderItemAdmin (admin.ModelAdmin):
    list_display = "order", "product", "name", "price", "quantity"
    search_fields = (
        "order",
        "product",
        "name",
    )

class OrderTabulareAdmin(admin.TabularInline):
    model = Order
    fields = (
        "requires_delivery",
        "status",
        "payment_on_get",
        "is_paid",
        "created_timestamp"
    )
    
    search_fields = (
        "requires_delivery",
        "payment_on_get",
        "is_paid",
        "created_timestamp"
    )
    readonly_fields = ("created_timestamp",)
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user_link",  # Кликабельная ссылка на заказ
        "requires_delivery",
        "status",
        "payment_on_get",
        "is_paid",
        "created_timestamp",
    )

    def user_link(self, obj):
        """
        Возвращает username пользователя с кликабельной ссылкой на редактирование текущего заказа.
        """
        url = reverse('admin:orders_order_change', args=[obj.id])  # URL для редактирования заказа
        username = obj.user.username if obj.user else "Анонимный"
        return format_html('<a href="{}">{}</a>', url, username)

    user_link.short_description = 'Пользователь'  # Заголовок для этого столбца

    search_fields = (
        "id",
        "user__username",  # Поиск по username
        "requires_delivery",
        "payment_on_get",
        "is_paid",
        "created_timestamp",
    )
    readonly_fields = ("created_timestamp",)
    list_filter = (
        "requires_delivery",
        "status",
        "payment_on_get",
        "is_paid",  
    )
    inlines = (OrderItemTabulareAdmin, )
