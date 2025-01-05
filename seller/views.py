from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework import permissions
from rest_framework.response import Response
from .services import get_or_create_seller
from .serializers import SellerSerializer, SellerProductSerializer
from products.models import Product
from itertools import chain, islice


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
        category_id = self.request.query_params.get("category_id")

        base_query = Product.objects.filter(seller=self.request.user)

        on_sale_query = base_query.filter(purchased_by__isnull=True)
        if category_id:
            on_sale_query = on_sale_query.filter(category_id=category_id)
        on_sale_query = on_sale_query.order_by("-added_at")

        sold_query = base_query.filter(purchased_by__isnull=False)
        if category_id:
            sold_query = sold_query.filter(category_id=category_id)
        sold_query = sold_query.order_by("-purchased_at")

        if self.request.query_params.get("status") == "on_sale":
            return on_sale_query
        if self.request.query_params.get("status") == "sold":
            return sold_query.all()[:50]

        return islice(chain(on_sale_query.all(), sold_query.all()), 50)
