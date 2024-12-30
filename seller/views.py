from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework import permissions
from rest_framework.response import Response
from .services import get_or_create_seller
from .serializers import SellerSerializer, SellerProductSerializer
from products.models import Product


class IsSeller(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_seller


class SellerView(APIView):
    permission_classes = (permissions.IsAuthenticated, IsSeller,)

    def get(self, request):
        seller = get_or_create_seller(request.user)
        serializer = SellerSerializer(instance=seller)
        return Response(serializer.data)


class SellerProductsView(ListAPIView):
    permission_classes = (permissions.IsAuthenticated, IsSeller,)
    serializer_class = SellerProductSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["seller"] = get_or_create_seller(self.request.user)
        return context

    def get_queryset(self):
        return Product.objects.filter(seller=self.request.user).order_by('-added_at').all()
