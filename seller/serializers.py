from rest_framework.serializers import ModelSerializer, SerializerMethodField, CharField
from .models import Seller
from .services import SellerStatsService, SellerEconomyService
from products.models import Product
from django.urls import reverse
from products.services import ProductFileManager


class SellerSerializer(ModelSerializer):
    on_sale = SerializerMethodField(read_only=True)
    paid = SerializerMethodField(read_only=True)

    class Meta:
        model = Seller
        fields = ("on_sale", "to_pay", "paid", "total_earned", "percent")
        read_only_fields = ("total_earned", "to_pay", "percent")

    def get_on_sale(self, seller: Seller):
        return SellerStatsService(seller).get_total_on_sale()

    def get_paid(self, seller: Seller):
        return SellerStatsService(seller).get_already_paid()


class SellerProductSerializer(ModelSerializer):
    file_name = SerializerMethodField(read_only=True)
    file_url = SerializerMethodField(read_only=True)
    category_name = CharField(read_only=True, source='category.name')
    price = SerializerMethodField(read_only=True)
    earn = SerializerMethodField(read_only=True)

    def get_file_url(self, product: Product) -> str | None:
        if ProductFileManager(product).has_file():
            return reverse("product-download", kwargs={"pk": product.id})
        return None

    def get_earn(self, product: Product):
        return SellerEconomyService(self.context["seller"]).get_earn(product)

    # по умолчанию price возвращается как строка
    def get_price(self, product: Product):
        return float(product.price)

    def get_file_name(self, product: Product):
        if product.file:
            return ProductFileManager.get_original_filename(product.file.name)
        return None

    class Meta:
        model = Product
        fields = ("id", "file_name", "file_url", "category_name", "price", "earn", "added_at", "purchased_at")
        read_only_fields = ("id", "file_name", "file_url", "category_name", "price", "earn", "added_at", "purchased_at")

