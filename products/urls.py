from django.urls import path
from products import views


urlpatterns = [
    path('', views.all_products, name='products'),
    # Will use url from setting url: product/product_id
    path('<product_id>', views.product_detail, name='product_detail'),
]
