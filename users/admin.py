from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    # ��������� ��������� ����� � ����� ������� ���������
    UserAdmin.fieldsets[0][1]["fields"] = (*UserAdmin.fieldsets[0][1]["fields"], "secret_phrase")
    add_fieldsets = UserAdmin.add_fieldsets + ((None, {"fields": ["secret_phrase"]}),)

admin.site.register(User, CustomUserAdmin)
