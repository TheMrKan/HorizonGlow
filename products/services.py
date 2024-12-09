from .models import Product
from users.models import User
from django.db import transaction
import datetime
import os.path
from django.db.models.fields.files import FieldFile


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


class ProductFileManager:

    product: Product
    new_file: FieldFile | None

    def __init__(self, product: Product, new_file: FieldFile | None):
        self.product = product
        self.new_file = new_file

    def update_file(self, commit=True):
        # удаление файла товара
        if not self.new_file:
            if self.product.file:
                self.product.file.delete(save=commit)
                self.product.file = None
            return

        new_file_orig_name = self.new_file.name
        self.new_file.name = self.__get_filename_for_storage(self.new_file.name)

        # если расширение нового и старого файла не совпадает, то создастся новый файл, а старый не удалится, поэтому удаляем явно
        if self.product.file and self.product.file.name != self.new_file.name:
            self.product.file.delete(save=False)
            self.product.file = None

        # на случай, если файл с оригинальным названием сохранился по какой-то причине (например формой)
        if not self.product.file and self.new_file.storage.exists(new_file_orig_name):
            self.new_file.storage.delete(new_file_orig_name)

        self.product.file = self.new_file

        if commit:
            self.product.save()

    def __get_filename_for_storage(self, original_name: str):
        """
        Возвращает имя файла продукта, под которым он будет храниться в хранилище (на диске)
        :return: <id продукта>.<расширение оригинального файла>
        """
        if self.product.id is None:
            raise RuntimeError("Unable to get filename before assigning the ID")

        path, ext = os.path.splitext(original_name)
        if not ext:
            raise NameError("Filename must have extension")
        return str(self.product.id) + ext


