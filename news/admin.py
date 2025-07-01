from django.contrib import admin
from django.db.models import ImageField
from image_uploader_widget.widgets import ImageUploaderWidget
from .models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    formfield_overrides = {
        ImageField: {"widget": ImageUploaderWidget},
    }
