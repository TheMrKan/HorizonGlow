from knox import views as knox_views
from .views import LoginView, RegisterView
from django.urls import path

urlpatterns = [
     path(r'register/', RegisterView.as_view(), name='register'),
     path(r'login/', LoginView.as_view(), name='knox_login'),
     path(r'logout/', knox_views.LogoutView.as_view(), name='knox_logout'),
     path(r'logoutall/', knox_views.LogoutAllView.as_view(), name='knox_logoutall'),
]