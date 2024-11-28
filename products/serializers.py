from rest_framework import serializers
from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField(source="get_products_count", read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', "products_count"]
        read_only_fields = ['id', 'name', "products_count"]


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'description', 'number', 'score', 'produced_at', 'price', 'category']
