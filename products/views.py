from rest_framework import viewsets, mixins, permissions, generics
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, NumberFilter


class CategoryViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    permission_classes = (permissions.IsAuthenticated,)

    queryset = Category.has_available_products.all()
    serializer_class = CategorySerializer


class ProductFilterSet(FilterSet):
    category = NumberFilter(field_name='category')

    class Meta:
        model = Product
        fields = ("category", )


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)

    queryset = Product.available.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilterSet
