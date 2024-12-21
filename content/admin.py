from django.contrib import admin
from .models import ContentModel


@admin.register(ContentModel)
class ContentAdmin(admin.ModelAdmin):
    pass
