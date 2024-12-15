import payments.nowpayments_api as api
from django.conf import settings
from users.models import User
from django.urls import reverse
from django.db import transaction
import traceback
from utils.urls import get_absolute_url
import decimal


class PaymentServiceInfoProvider:

    @classmethod
    def get_min_payment_amount(cls):
        return settings.PAYMENT_MIN_AMOUNT


class TopupProcessor:

    class InvalidAmountError(Exception):
        pass

    class PaymentServiceInteractionError(Exception):
        pass

    class InvalidOrderIdError(Exception):
        pass

    @classmethod
    def request_topup(cls, user: User, amount: float) -> str:
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
    def update_topup_status(cls, order_id: str, status: str, amount: float):
        if status != "finished":
            return

        with transaction.atomic(using="serializeable"):
            try:
                user = User.objects.get(id=int(order_id))
            except User.DoesNotExist:
                raise cls.InvalidOrderIdError

            user.balance += decimal.Decimal(amount)
            user.save()
        print(f"Updated balance of user {user.id}: {amount} (new balance: {user.balance})")


