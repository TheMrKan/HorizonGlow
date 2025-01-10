from django.contrib import admin
from django.urls import path, include
from utils.success_handler import return_code

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),
    path('api/', include('products.urls')),
    path('api/payment/', include("payments.urls")),
    path('api/content/', include("content.urls")),
    path('api/seller/', include("seller.urls")),
    path('api/news/', include("news.urls")),
    path('api/return/<int:code>/', return_code, name='return_code'),
]
