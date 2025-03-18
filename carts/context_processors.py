from carts.models import CartItem

def cart_count(request):
    if request.user.is_authenticated:
        count = CartItem.objects.filter(cart__user=request.user).distinct().count()  
    else:
        count = 0  
    return {"cart_count": count}
