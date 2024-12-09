import time
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.db.models.fields.files import FieldFile
from .models import Category, Product
from .services import ProductFileManager


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


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
        self.old_file = self.instance.file if self.instance else None
        return self.cleaned_data.get("file", None)

    def save(self, commit=True):
        new_file = self.instance.file    # файл записывается в instance до вызова save
        self.instance.file = None    # установка в None позволяет избежать сохранения "сырого" файла в следующей строчке

        # если instance.id = None, то модель нужно сохранить в БД для получения id, который используется в get_filename_for_storage
        super().save(commit=self.instance.id is None)

        # приводим модель в состояние, не тронутое формой, т. к. сервис может быть вызван из DRF view
        self.instance.file = self.old_file
        try:
            ProductFileManager(self.instance, new_file).update_file(commit=False)
        except Exception as e:
            raise ValidationError(str(e))

        if commit:
            self.instance.save()

        return self.instance


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["description", "category", "number", "score", "price", "purchased_by"]
    form = ProductAdminForm

