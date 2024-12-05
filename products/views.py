from rest_framework import viewsets, mixins, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from utils.exceptions import APIException
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from .services import ProductBuyer
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

    @action(detail=True, methods=['post'])
    def buy(self, request, pk=None):
        product = self.get_object()

        try:
            ProductBuyer(product.id, request.user.id).buy()
            return Response(data={}, status=status.HTTP_200_OK)
        except ProductBuyer.AlreadyBoughtError:
            raise APIException('Product already bought', code="already_bought", status=status.HTTP_409_CONFLICT)
        except ProductBuyer.InsufficientBalanceError:
            raise APIException('Insufficient balance', code="insufficient_balance", status=status.HTTP_409_CONFLICT)
        except Exception as e:
            raise APIException(detail=str(e), code=status.HTTP_500_INTERNAL_SERVER_ERROR)

