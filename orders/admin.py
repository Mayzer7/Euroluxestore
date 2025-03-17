from django.contrib import admin
from django.contrib.admin.filters import DateFieldListFilter
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price')

    def has_delete_permission(self, request, obj=None):
        """Запрещаем удаление товаров из заказа."""
        return False


from django.db.models import Sum
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'display_user', 'total_price', 'total_items', 'status', 'delivery_method', 'created_at')
    list_filter = ('status', ('created_at', DateFieldListFilter), 'delivery_method')
    search_fields = ('user__username', 'email', 'phone')
    inlines = [OrderItemInline]
    ordering = ['-created_at']  # Можно поменять порядок по умолчанию

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(total_items_count=Sum('items__quantity'))  # Аннотация количества товаров

    def total_items(self, obj):
        return obj.total_items_count or 0
    total_items.short_description = "Всего товаров"
    total_items.admin_order_field = 'total_items_count'  # Позволяет сортировать по количеству товаров

    def display_user(self, obj):
        return obj.user.username if obj.user else "Аноним"
    display_user.short_description = "Пользователь"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    list_filter = ('order__user',)
    search_fields = ('product__name', 'order__user__username')
    ordering = []  # Динамическая сортировка
