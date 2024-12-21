from django.urls import path
from .views import ContentView


urlpatterns = [
    path(r"", ContentView.as_view(), name="content")
]