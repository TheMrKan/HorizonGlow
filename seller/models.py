from django.db import models
from users.models import User


class Seller(models.Model):
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE, related_name='seller')
    percent = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    """
    Процент селлера
    """
    total_earned = models.DecimalField("Total earned", max_digits=8, decimal_places=2, default=0)
    """
    Общая сумма, полученная селлером с продажи товаров за всё время
    """
    to_pay = models.DecimalField("To pay", max_digits=8, decimal_places=2, default=0)
    """
    Сумма, которую сайт еще не выплатил селлеру
    """

    def __str__(self):
        return self.user.username

    def __repr__(self):
        return self.__str__()
