from .views import *
from django.urls import path
from rest_framework.routers import DefaultRouter

urlpatterns = [
     path(r'auth/register/', RegisterView.as_view(), name='register'),
     path(r'auth/login/', LoginView.as_view(), name='knox_login'),
     path(r'auth/logout/', LogoutView.as_view(), name='knox_logout'),
     path(r'account/', AccountView.as_view(), name='account'),
     path(r'account/purchases/', PurchasesView.as_view(), name='purchases')
]