import os
from django.apps import AppConfig
import sys


class MyAppConfig(AppConfig):
    name = 'analytics'

    def ready(self):
        if "manage.py" in sys.argv and "runserver" not in sys.argv:
            return

        from analytics.services import GoogleSheetsWriter

        if os.environ.get('RUN_MAIN'):
            GoogleSheetsWriter()    # создание объекта для синглтона. Создание занимает несколько секунд
