from django.urls import path
from .views import SellerView, SellerProductsView

urlpatterns = [
    path('', SellerView.as_view(), name='seller'),
    path('products/', SellerProductsView.as_view(), name='seller_products')
]