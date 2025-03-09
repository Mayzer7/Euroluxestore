from .models import Categories

def categories_processor(request):
    return {'categories': Categories.objects.all()}
