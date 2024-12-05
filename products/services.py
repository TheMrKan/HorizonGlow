from .models import Product
from users.models import User
from django.db import transaction
import datetime


class ProductBuyer:
    """
    Сервисный объект для покупки товара пользователем.
    buy() выполняется с уровнем изоляции Serializeable, чтобы избежать аномалий.
    Конструктор принимает ID и загружает объекты внутри, чтобы они отслеживались транзакцией с нужным уровнем изоляции
    """
    product_id: int
    user_id: str

    product: Product
    user: User

    class InsufficientBalanceError(Exception):
        pass

    class AlreadyBoughtError(Exception):
        pass

    def __init__(self, product_id: int, user_id: str):
        self.product_id = product_id
        self.user_id = user_id

    def buy(self):
        with transaction.atomic(using="serializeable"):
            self.__load_entities()
            self.__assert_can_buy()

            self.product.purchased_by = self.user
            self.product.purchased_at = datetime.datetime.now()
            self.user.balance -= self.product.price
            self.product.save()
            self.user.save()

    def __load_entities(self):
        self.product = Product.objects.get(id=self.product_id)
        self.user = User.objects.get(id=self.user_id)

    def __assert_can_buy(self):
        if self.product.purchased_by:
            raise self.AlreadyBoughtError

        if self.user.balance < self.product.price:
            raise self.InsufficientBalanceError

