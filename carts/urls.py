from django.urls import path
from .views import add_to_cart, cart_view, cart_count

app_name = "carts"

urlpatterns = [
    path("add/<int:product_id>/", add_to_cart, name="add_to_cart"),
    path('cart/', cart_view, name='cart_view'),
    path('cart-count/', cart_count, name='cart_count'),
]
