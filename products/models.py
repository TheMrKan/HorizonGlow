from django.db import models
from users.models import User


class HasAvailableProductsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(products__isnull=False, products__purchased_by__isnull=True).distinct()


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

    has_available_products = HasAvailableProductsManager()

    def get_products_count(self):
        return self.products.filter(purchased_by__isnull=True).distinct().count()


class AvailableManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(purchased_by=None)


class Product(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, null=False, related_name='selling_products')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=False, related_name='products')
    description = models.CharField(max_length=400)
    number = models.CharField(max_length=8)
    score = models.CharField(max_length=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    produced_at = models.DateTimeField()
    added_at = models.DateTimeField(auto_now_add=True)
    purchased_at = models.DateTimeField(null=True)
    purchased_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='purchased_products')

    available = AvailableManager()
