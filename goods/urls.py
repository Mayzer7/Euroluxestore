from django.urls import path
from goods import views

app_name = 'goods'

urlpatterns = [
    path('catalog/', views.CatalogView.as_view(), name='catalog'),
    path('catalog/<slug:category_slug>/', views.CatalogView.as_view(), name='catalog_by_category'),
    path('product/', views.ProductView.as_view(), name='product'),
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    # path('search', views.CatalogView.as_view(), name='search'),
    # path('<slug:category_slug>/', views.CatalogView.as_view(), name='index'),
    # path('product/<slug:product_slug>/', views.ProductView.as_view(), name='product_detail'),
]