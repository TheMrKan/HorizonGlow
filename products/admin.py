import time
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.db.models.fields.files import FieldFile
from django.db.models import FileField
from django.contrib.admin.widgets import AdminFileWidget
from .models import Category, Product
from .services import ProductFileManager
from django.urls import reverse


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


class MockFileForWidgetRender:
    filename: str
    url: str

    def __init__(self, filename: str, url: str):
        self.filename = filename
        self.url = url

    def __str__(self):
        return self.filename

    def __repr__(self):
        return self.__str__()


class ProductFileInputWidget(AdminFileWidget):
    def format_value(self, value):
        """
        Переопределяем получение ссылки на скачивание файла в строке "Currently: <название файла>"
        """
        file: FieldFile | None = super().format_value(value)
        if file:
            product_id = ProductFileManager.get_product_id_from_filename(file.name)
            url = reverse("product-download", kwargs={"pk": product_id})
            return MockFileForWidgetRender(file.name, url)
        return None


class ProductAdminForm(ModelForm):
    """
    Форма для Product в админ-панели. Переопределена, чтобы делегировать управление файлом на сервис
    """

    old_file: FieldFile | None = None
    """
    Объект файла до применения обновлений из формы. Нужен, чтобы сервис мог удалить прошлый файл
    """

    class Meta:
        fields = "__all__"

    # по какой-то причине Django вызывает этот метод после save(), но не добавляет его перед этим
    def save_m2m(self):
        pass

    def clean_file(self):
        new_file: FieldFile | None = self.cleaned_data.get("file", None)

        try:
            ProductFileManager.validate_file(new_file)
        except ProductFileManager.InvalidFileTypeError:
            raise ValidationError(f"Invalid file type. Allowed types: {', '.join(ProductFileManager.ALLOWED_EXTENSIONS)}", code="invalid_type")
        except ProductFileManager.FileTooLargeError:
            raise ValidationError(f"File is too large. Max bytes: {ProductFileManager.MAX_FILE_SIZE_BYTES}", "too_large")

        self.old_file = self.instance.file if self.instance else None
        return new_file

    def save(self, commit=True):
        new_file = self.instance.file    # файл записывается в instance до вызова save
        self.instance.file = None    # установка в None позволяет избежать сохранения "сырого" файла в следующей строчке

        # если instance.id = None, то модель нужно сохранить в БД для получения id, который используется в get_filename_for_storage
        super().save(commit=self.instance.id is None)

        # приводим модель в состояние, не тронутое формой, т. к. сервис может быть вызван из DRF view
        self.instance.file = self.old_file

        ProductFileManager(self.instance).update_file(new_file, commit=False, bypass_validation=True)

        if commit:
            self.instance.save()

        return self.instance


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["description", "category", "number", "score", "price", "purchased_by"]

    form = ProductAdminForm
    formfield_overrides = {
        FileField: {"widget": ProductFileInputWidget},
    }


