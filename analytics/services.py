import gspread.utils
from gspread import Client, service_account, Spreadsheet, Worksheet
from typing import Self
from django.conf import settings

from products.models import Product
from seller.services import SellerEconomyService


class GoogleSheetsWriter:

    # static
    __instance: Self = None

    __client: Client
    __table: Spreadsheet
    __worksheet: Worksheet

    HEADER = ["Селлер", "Дата загрузки", "Имя файла", "Категория файла", "Score", "Number", "Цена продажи", "Цена селлера", "Дата продажи", "Покупатель"]

    # примитивный Singleton
    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
            cls.__instance.__initialize()
        return cls.__instance

    def __initialize(self):
        print("Initializing GoogleSheetsWriter...")
        self.__client = service_account("google_sheets_auth.json")
        self.__table = self.__client.open_by_key(settings.GOOGLE_TABLE_ID)
        self.__sheet = self.__table.get_worksheet(0)

        if self.__sheet.id == 0:
            print("Creating sheet...")
            self.__sheet = self.__create_sheet()

        print("GoogleSheetsWriter initialization completed")

    def __create_sheet(self):
        sheet = self.__table.add_worksheet("Продажи товаров", 1, len(self.HEADER), 0)
        sheet.update([self.HEADER], "A1")
        sheet.format("A1:Z1", {"textFormat": {"bold": True}})

        sheet.append_row([" ", " "])    # freeze не работает, если в таблице всего 1 строка
        sheet.format("A2:Z2", {"textFormat": {"bold": False}})

        sheet.freeze(1)
        return sheet

    def log_purchase(self, product: Product):
        # чтобы избежать циклического импорта
        from products.services import ProductFileManager

        if product.file:
            filename = ProductFileManager.get_original_filename(product.file.name)
        else:
            filename = "None"

        earn = float(SellerEconomyService(product.seller.seller).get_earn(product))
        added = product.added_at.strftime("%Y-%m-%d %H:%M:%S")
        purchased = product.purchased_at.strftime("%Y-%m-%d %H:%M:%S")

        self.__sheet.append_row([product.seller.username, added, filename, product.category.name,
                                product.score, product.number, float(product.price), earn, purchased, product.purchased_by.username],
                                value_input_option=gspread.utils.ValueInputOption.user_entered)
