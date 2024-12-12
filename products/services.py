from .models import Product
from users.models import User
from django.db import transaction
import datetime
import os.path
from django.db.models.fields.files import FieldFile
from typing import List
from django.conf import settings
from django.utils import timezone
import traceback


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

    class BuyingBySellerError(Exception):
        pass

    class NoFileError(Exception):
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
        if not ProductFileManager(self.product).has_file():
            raise self.NoFileError

        if self.product.seller == self.user:
            raise self.BuyingBySellerError

        if self.product.purchased_by:
            raise self.AlreadyBoughtError

        if self.user.balance < self.product.price:
            raise self.InsufficientBalanceError


class ProductFileManager:
    ALLOWED_EXTENSIONS = {'.zip', '.rar', '.7z'}
    MAX_FILE_SIZE_BYTES = 1024 * 1024 * 10    # 10 МБ
    SAFE_NAME = "upload"

    product: Product

    class InvalidFileTypeError(Exception):
        extension: str

        def __init__(self, extension: str):
            self.extension = extension
            super().__init__(f'Invalid file type: {extension}')

    class FileTooLargeError(Exception):
        pass

    def __init__(self, product: Product):
        self.product = product

    @classmethod
    def validate_file(cls, file: FieldFile | None, set_safe_name=True):
        if file is None:
            return

        path, ext = os.path.splitext(file.name)
        if ext not in cls.ALLOWED_EXTENSIONS:
            raise cls.InvalidFileTypeError(ext)

        if file.size > cls.MAX_FILE_SIZE_BYTES:
            raise cls.FileTooLargeError

        if set_safe_name:
            cls.set_safe_name(file)

    @classmethod
    def set_safe_name(cls, file: FieldFile | None):
        """
        Заменяет название файла на константу, сохраняя оригинальное расширение.
        Должен быть вызван на этапе валидации файла
        В формах файл может сохраняться сразу после валидации, что может быть использовано для повреждения файлов других товаров, т. к. в хранилище включена перезапись
        Пример: при загрузке пустого архива '12.zip', если он будет сохранен не сервисом, то он перезапишет существующий файл товара с ID 12.

        """
        name, ext = os.path.splitext(file.name)
        file.name = cls.SAFE_NAME + ext

    @staticmethod
    def get_product_id_from_filename(filename: str) -> int:
        name, ext = os.path.splitext(filename)
        return int(name)

    def has_file(self):
        return bool(self.product.file) and self.product.file.storage.exists(self.product.file.name)

    def update_file(self, new_file: FieldFile | None, commit=True, bypass_validation=False):
        if not bypass_validation:
            self.validate_file(new_file)

        # удаление файла товара
        if not new_file:
            if self.product.file:
                self.product.file.delete(save=commit)
                self.product.file = None
            return

        new_file_orig_name = new_file.name
        new_file.name = self.__get_filename_for_storage(new_file.name)

        # если расширение нового и старого файла не совпадает, то создастся новый файл, а старый не удалится, поэтому удаляем явно
        if self.product.file and self.product.file.name != new_file.name:
            self.product.file.delete(save=False)
            self.product.file = None

        # на случай, если файл с оригинальным названием сохранился по какой-то причине (например формой)
        if not self.product.file and new_file.storage.exists(new_file_orig_name):
            new_file.storage.delete(new_file_orig_name)

        self.product.file = new_file

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


class ProductFileCleaner:
    def __init__(self):
        pass

    @staticmethod
    def prune_outdated_files() -> List[str]:
        """
        Удаляет файлы для всех продуктов, купленых более settings.PRODUCT_FILE_MAX_AGE времени назад
        :return: Список названий удаленных файлов
        """

        expired = timezone.now() - settings.PRODUCT_FILE_MAX_AGE
        products = Product.objects.filter(file__isnull=False).exclude(file__exact='').filter(purchased_at__lte=expired)

        result = []
        for product in products:
            try:
                deleted_file = product.file.name
                ProductFileManager(product).update_file(None)
                result.append(deleted_file)
                print(f"[PRUNE] Deleted file {deleted_file} of product {product}")
            except:
                traceback.print_exc()
        return result
