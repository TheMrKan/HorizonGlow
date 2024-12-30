from django.db.transaction import commit
from rest_framework import viewsets, mixins, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.renderers import BaseRenderer
from utils.exceptions import APIException
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from .services import ProductBuyer, ProductFileManager, ProductAccessManager, ProductDeleter
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, NumberFilter
from django.http.response import FileResponse
import os.path


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


class CanDownload(permissions.BasePermission):
    def has_object_permission(self, request, view, product: Product):
        if not isinstance(product, Product):
            raise TypeError("Unsupported object type: %s" % type(product))

        return ProductAccessManager(product, request.user).can_download()


class CanUpdateFile(permissions.BasePermission):
    def has_object_permission(self, request, view, product: Product):
        if not isinstance(product, Product):
            raise TypeError("Unsupported object type: %s" % type(product))

        return ProductAccessManager(product, request.user).can_update_file()


class ProductViewSet(viewsets.ReadOnlyModelViewSet, mixins.CreateModelMixin, mixins.DestroyModelMixin):
    permission_classes = (permissions.IsAuthenticated, )

    queryset = Product.available.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilterSet

    # Product.objects.all() для метода DELETE
    def get_queryset(self):
        if self.action == "destroy":
            return Product.objects.all()
        return super().get_queryset()

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
        except ProductBuyer.BuyingBySellerError:
            raise APIException("You can't buy the product you are selling", code="buying_by_seller", status=status.HTTP_409_CONFLICT)
        except ProductBuyer.NoFileError:
            raise APIException(detail="File for this product hasn't been added yet or has already been deleted", code="no_file", status=status.HTTP_409_CONFLICT)
        except Exception as e:
            raise APIException(detail=str(e), code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True,
            methods=['get'],
            queryset=Product.objects.all(),
            permission_classes=(*permission_classes, CanDownload))
    def download(self, request, pk=None):
        product: Product = self.get_object()

        if not ProductFileManager(product).has_file():
            raise APIException(detail="File for this product hasn't been added yet or has already been deleted", code="no_file", status=status.HTTP_409_CONFLICT)

        file_handle = product.file.open()

        response = FileResponse(file_handle, content_type='whatever')
        response['Content-Length'] = product.file.size

        filename = ProductFileManager.get_original_filename(product.file.name)
        response['Content-Disposition'] = 'attachment; filename="%s"' % filename

        return response

    @action(detail=True,
            methods=['put'],
            queryset=Product.objects.all(),
            permission_classes=(*permission_classes, CanUpdateFile))
    def upload(self, request, pk=None):
        product: Product = self.get_object()

        file = request.FILES.get('file')
        try:
            ProductFileManager(product).update_file(file, commit=True, bypass_validation=False, allow_delete=ProductAccessManager(product, request.user).can_delete_file())
            return Response(data={}, status=status.HTTP_202_ACCEPTED)
        except ProductFileManager.InvalidFileTypeError as e:
            raise APIException(detail=str(e), code="invalid_file_type", status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        except ProductFileManager.FileTooLargeError as e:
            raise APIException(detail=str(e), code="file_too_large", status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
        except ProductFileManager.DeleteNotAllowedError as e:
            raise APIException(detail=str(e), code="delete_not_allowed", status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

    def perform_destroy(self, instance):
        try:
            ProductDeleter(instance).delete()
        except ProductDeleter.AlreadyBoughtError as e:
            raise APIException(str(e), code="already_bought", status=status.HTTP_409_CONFLICT)
