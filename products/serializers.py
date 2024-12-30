from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Category, Product
from .services import ProductCreator
from .validators import *


class CategorySerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField(source="get_products_count", read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', "products_count"]
        read_only_fields = ['id', 'name', "products_count"]


class ProductSerializer(serializers.ModelSerializer):
    """
    Поля валилируются через методы, т. к. при обычном использовании валидаторы не могут изменять значение
    """

    class Meta:
        model = Product
        fields = ['id', 'description', 'category', 'number', 'score', 'produced_at', 'price']
        read_only_fields = ["id"]
        validators = []

    def validate_description(self, value):
        return DescriptionValidator()(value)

    def validate_number(self, value):
        return NumberValidator()(value)

    def validate_score(self, value):
        return ScoreValidator()(value)

    def validate_price(self, value):
        return PriceValidator()(value)

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

