from rest_framework.urls import path
from .views import PaymentServiceInfo, TopupView

urlpatterns = [
    path(r'', PaymentServiceInfo.as_view(), name='payment'),
    path(r"topup/", TopupView.as_view(), name="topup")
]