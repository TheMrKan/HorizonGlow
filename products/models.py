from django.db import models
from users.models import User


class HasAvailableProductsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(products__isnull=False, products__purchased_by__isnull=True).distinct()


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

    objects = models.Manager()
    has_available_products = HasAvailableProductsManager()

    class Meta:
        verbose_name_plural = "categories"

    def get_products_count(self):
        return self.products.filter(purchased_by__isnull=True).distinct().count()

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


class AvailableManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(purchased_by=None).exclude(file__isnull=True).exclude(file__exact='')


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
    purchased_at = models.DateTimeField(null=True, default=None, blank=True)
    purchased_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, default=None, blank=True, related_name='purchased_products')
    file = models.FileField(null=True, default=None, blank=True)

    objects = models.Manager()
    available = AvailableManager()

    def __str__(self):
        return self.description

    def __repr__(self):
        return self.__str__()
