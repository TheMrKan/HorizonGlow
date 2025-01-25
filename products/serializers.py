from rest_framework import serializers
from rest_framework.fields import CharField, SerializerMethodField
from .models import Category, Product
from .services import ProductCreator, ProductSupportService
from .validators import *
from users.models import User


class CategorySerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField(source="get_products_count", read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', "description_url", "products_count"]
        read_only_fields = ['id', 'name', "description_url", "products_count"]


class ProductSerializer(serializers.ModelSerializer):
    """
    Поля валилируются через методы, т. к. при обычном использовании валидаторы не могут изменять значение
    """

    support_info_fields = {"support_code": SerializerMethodField(read_only=True),
                           "is_support_period_expired": SerializerMethodField(read_only=True),
                           "purchased_at": SerializerMethodField(read_only=True),
                           "purchased_by": SerializerMethodField(read_only=True),}

    def get_fields(self):
        fields: dict = super().get_fields()
        user = self.context["request"].user
        if user and self.__can_read_support_info(user):
            fields.update(self.support_info_fields)
        return fields

    @staticmethod
    def __can_read_support_info(user: User) -> bool:
        return user.has_perm("products.read_support_info")

    class Meta:
        model = Product
        fields = ['id', 'description', 'category', 'number', 'score', 'produced_at', 'price']
        read_only_fields = ["id"]
        validators = []

    @staticmethod
    def validate_description(value):
        return DescriptionValidator()(value)

    @staticmethod
    def validate_number(value):
        return NumberValidator()(value)

    @staticmethod
    def validate_score(value):
        return ScoreValidator()(value)

    @staticmethod
    def validate_price(value):
        return PriceValidator()(value)

    @staticmethod
    def get_is_support_period_expired(instance: Product):
        return ProductSupportService(instance).is_support_period_expired()

    # AssertionError: It is redundant to specify `source='support_code'` on field 'CharField' in serializer 'ProductSerializer'...
    # если использовать CharField в support_info_fields
    @staticmethod
    def get_support_code(instance: Product):
        return instance.support_code

    @staticmethod
    def get_purchased_at(instance: Product):
        return instance.purchased_at

    @staticmethod
    def get_purchased_by(instance: Product):
        return instance.purchased_by_id if instance.purchased_by else None

    def create(self, validated_data):
        try:
            product = ProductCreator(
                validated_data['seller'],
                validated_data['description'],
                validated_data['category'],
                validated_data['number'],
                validated_data['score'],
                validated_data['produced_at'],
                validated_data['price']
            ).create()
        except ProductCreator.InvalidSellerError as e:
            raise serializers.ValidationError(e)

        return product
