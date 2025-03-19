from django.urls import path
from .views import add_to_cart, remove_from_cart ,cart_view, cart_count

app_name = "carts"

urlpatterns = [
    path("add/<int:product_id>/", add_to_cart, name="add_to_cart"),
    path("remove/<int:item_id>/", remove_from_cart, name="remove_from_cart"),
    path('', cart_view, name='cart_view'),
    path('cart-count/', cart_count, name='cart_count'),
]
