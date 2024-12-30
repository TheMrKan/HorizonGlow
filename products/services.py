from datetime import datetime

from .models import Product, Category
from users.models import User
from django.db import transaction
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
            self.product.purchased_at = timezone.now()
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


class ProductAccessManager:
    product: Product
    user: User

    def __init__(self, product: Product, user: User):
        self.product = product
        self.user = user

    def can_download(self) -> bool:
        # в т. ч. обеспечивает доступ админ-аккаунтам
        if self.user.has_perm('products.download_all_products'):
            return True

        # разрешаем селлеру и пользователю, купившему товар
        if self.product.purchased_by == self.user or self.product.seller == self.user:
            return True

        return False

    def can_update_file(self) -> bool:
        # в т. ч. обеспечивает доступ админ-аккаунтам. Если доступ по перму, то можно обновлять существующий файл
        if self.user.has_perm('products.upload_all_products'):
            return True

        # обновить может только селлер
        if self.product.seller != self.user:
            return False

        # селлер не может обновить файл после первой загрузки (создания товара)
        if ProductFileManager(self.product).has_file():
            return False

        return True

    def can_delete_file(self) -> bool:
        # в т. ч. обеспечивает доступ админ-аккаунтам
        if self.user.has_perm('products.upload_all_products'):
            return True

        # удалять файл может только админ
        return False

    def can_delete_product(self) -> bool:
        # в т. ч. обеспечивает доступ админ-аккаунтам
        if self.user.has_perm('products.delete_all_products'):
            return True

        # удалить может только селлер
        return self.product.seller == self.user


class ProductFileManager:
    ALLOWED_EXTENSIONS = {'.zip', '.rar', '.7z'}
    MAX_FILE_SIZE_BYTES = 1024 * 1024 * 10    # 10 МБ
    UPLOAD_PREFIX = "upload__"

    product: Product

    class InvalidFileTypeError(Exception):
        extension: str

        def __init__(self, extension: str):
            self.extension = extension
            super().__init__(f'Invalid file type: {extension}')

    class FileTooLargeError(Exception):
        pass

    class DeleteNotAllowedError(Exception):
        pass

    def __init__(self, product: Product):
        self.product = product

    @classmethod
    def validate_file(cls, file: FieldFile | None, set_safe_name=True, allow_delete=True):
        if file is None:
            if not allow_delete:
                raise cls.DeleteNotAllowedError
            return None

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
        Добавляет префикс в название файла
        Должен быть вызван на этапе валидации файла
        В формах файл может сохраняться сразу после валидации, что может быть использовано для повреждения файлов других товаров, т. к. в хранилище включена перезапись
        Пример: при загрузке пустого архива '12.zip', если он будет сохранен не сервисом, то он перезапишет существующий файл товара с ID 12.

        """
        file.name = cls.UPLOAD_PREFIX + file.name

    @staticmethod
    def get_product_id_from_filename(filename: str) -> int:
        splitted = filename.split("__", 1)
        if splitted[0].isdigit():
            return int(splitted[0])
        else:
            last_digit = -1
            for char in splitted[0]:
                if char.isdigit():
                    last_digit += 1
                else:
                    break
            if last_digit == -1:
                raise NameError(f"Failed to extract product id from filename '{filename}'")
            return int(splitted[0][:last_digit+1])

    @staticmethod
    def get_original_filename(storage_filename: str):
        splitted = storage_filename.split("__", 1)
        if len(splitted) > 1:
            return splitted[1]
        return splitted[0]

    def has_file(self):
        return bool(self.product.file) and self.product.file.storage.exists(self.product.file.name)

    def update_file(self, new_file: FieldFile | None, commit=True, bypass_validation=False, allow_delete=True):
        if not bypass_validation:
            self.validate_file(new_file, allow_delete=allow_delete)

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

        # InMemoryUploadedFile не имеет storage, соответственно проверять сохранение файла не нужно
        # InMemoryUploadedFile используется при загрузке в панель, TemporaryUploadedFile при загрузке через админку
        if hasattr(new_file, "storage"):
            # на случай, если файл с оригинальным названием сохранился по какой-то причине (например формой)
            if not self.product.file and new_file.storage.exists(new_file_orig_name):
                new_file.storage.delete(new_file_orig_name)

        self.product.file = new_file

        if commit:
            self.product.save()

    def __get_filename_for_storage(self, original_name: str):
        """
        Возвращает имя файла продукта, под которым он будет храниться в хранилище (на диске)
        :return: <id продукта>__<название оригинального файла>.<расширение оригинального файла>
        """
        if self.product.id is None:
            raise RuntimeError("Unable to get filename before assigning the ID")

        original_name = original_name.replace(self.UPLOAD_PREFIX, '', 1)

        if not original_name:
            raise NameError("Empty file name is not allowed")

        return f"{self.product.id}__" + original_name


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


class ProductCreator:
    """
    Сервис не проверяет валидность полей, кроме seller. Валидаторы должны быть вызваны из .validators ранее
    """

    class InvalidSellerError(Exception):
        def __init__(self, *args):
            super().__init__(*args)

    seller: User
    description: str
    category: Category
    number: str
    score: str
    produced_at: datetime
    price: float

    def __init__(self, seller: User, description: str, category: Category, number: str, score: str, produced_at: datetime, price: float):
        self.seller = seller
        self.description = description
        self.category = category
        self.number = number
        self.score = score
        self.produced_at = produced_at
        self.price = price

    def create(self) -> Product:
        self.assert_seller_valid()

        product = Product(seller=self.seller, description=self.description, category=self.category,
                          number=self.number, score=self.score, produced_at=self.produced_at, price=self.price)
        product.save()
        return product

    def assert_seller_valid(self):
        if not self.seller.is_seller:
            raise self.InvalidSellerError("User is not a seller")


class ProductDeleter:
    product: Product

    class AlreadyBoughtError(Exception):
        def __init__(self):
            super().__init__("Can't delete purchased product")

    def __init__(self, product: Product):
        self.product = product

    def delete(self):
        self.assert_can_be_deleted()

        # на всякий случай явно удаляем файл
        ProductFileManager(self.product).update_file(None, commit=True, bypass_validation=True)

        self.product.delete()

    def assert_can_be_deleted(self):
        if self.product.purchased_by:
            raise self.AlreadyBoughtError()
