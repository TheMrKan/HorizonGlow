from rest_framework import viewsets, mixins, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.renderers import BaseRenderer
from utils.exceptions import APIException
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from .services import ProductBuyer
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, NumberFilter
from django.http.response import FileResponse


class CategoryViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    permission_classes = (permissions.IsAuthenticated,)

    queryset = Category.has_available_products.all()
    serializer_class = CategorySerializer


class ProductFilterSet(FilterSet):
    category = NumberFilter(field_name='category')

    class Meta:
        model = Product
        fields = ("category", )


class PassthroughRenderer(BaseRenderer):
    """
        Return data as-is. View should supply a Response.
    """
    media_type = ''
    format = ''

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data


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

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        product = self.get_object()

        file_handle = product.file.open()

        response = FileResponse(file_handle, content_type='whatever')
        response['Content-Length'] = product.file.size
        response['Content-Disposition'] = 'attachment; filename="%s"' % product.file.name

        return response


