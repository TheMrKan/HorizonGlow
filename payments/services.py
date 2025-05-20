import payments.nowpayments_api as api
from django.conf import settings
from users.models import User
from django.urls import reverse
from django.db import transaction
import traceback
from utils.urls import get_absolute_url
import decimal
from typing import NewType


class PaymentServiceInfoProvider:

    @classmethod
    def get_min_payment_amount(cls):
        return settings.PAYMENT_MIN_AMOUNT


USDAmount = NewType('USDAmount', float)
CryptoCurrencyAmount = NewType('CryptoCurrencyAmount', float)


class TopupProcessor:

    class InvalidAmountError(Exception):
        pass

    class PaymentServiceInteractionError(Exception):
        pass

    class InvalidOrderIdError(Exception):
        pass

    @classmethod
    def request_topup(cls, user: User, amount: USDAmount) -> str:
        if amount < PaymentServiceInfoProvider.get_min_payment_amount():
            raise cls.InvalidAmountError

        try:
            invoice = api.create_invoice(
                settings.PAYMENT_SERVICE_API_KEY,
                amount,
                "usd",
                callback_url=get_absolute_url(reverse("nowpayments-ipn")),
                order_id=str(user.id),
                success_url=get_absolute_url("topup/success"),
                cancel_url=get_absolute_url("topup/fail")
            )

            return invoice.invoice_url
        except Exception as e:
            traceback.print_exc()
            raise cls.PaymentServiceInteractionError from e

    @classmethod
    def update_topup_status(cls,
                            order_id: str,
                            status: str,
                            actually_paid_in_currency: CryptoCurrencyAmount,
                            target_amount_in_currency: CryptoCurrencyAmount,
                            target_amount_in_usd: USDAmount):
        if status not in ("partially_paid", "finished"):
            return

        with transaction.atomic(using="serializeable"):
            try:
                user = User.objects.get(id=int(order_id))
            except User.DoesNotExist:
                raise cls.InvalidOrderIdError

            actually_paid_in_usd: USDAmount = USDAmount(target_amount_in_usd * (actually_paid_in_currency / target_amount_in_currency))

            user.balance += decimal.Decimal(actually_paid_in_usd)
            user.save()
        print(f"Updated balance of user {user.id}: {actually_paid_in_usd} (new balance: {user.balance})")


