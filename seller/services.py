from .models import Seller
from users.models import User
from content.models import ContentModel
from products.models import Product
from django.db.models import Sum


def get_or_create_seller(user: User):
    if hasattr(user, 'seller'):
        return user.seller

    return SellerCreator(user).create()


class SellerCreator:
    user: User

    def __init__(self, user: User):
        self.user = user

    def create(self):
        self.user.seller = Seller()
        self.user.seller.percent = self.get_default_percent()
        self.user.seller.save()

    @staticmethod
    def get_default_percent() -> float:
        return float(ContentModel.objects.get(pk="seller_percent_default").value)


class SellerStatsService:
    seller: Seller

    def __init__(self, seller: Seller):
        self.seller = seller

    def get_total_on_sale(self):
        return float(Product.objects.filter(seller_id=self.seller.user_id, purchased_by__isnull=True).aggregate(Sum('price'))["price__sum"])

    def get_already_paid(self):
        return float(self.seller.total_earned - self.seller.to_pay)


class SellerEconomyService:
    seller: Seller

    def __init__(self, seller: Seller):
        self.seller = seller

    def get_earn(self, product: Product):
        return product.price * (100 - self.seller.percent) / 100

    def on_product_purchased(self, product: Product, commit=True):
        earn = self.get_earn(product)
        self.seller.total_earned += earn
        self.seller.to_pay += earn

        if commit:
            self.seller.save()

