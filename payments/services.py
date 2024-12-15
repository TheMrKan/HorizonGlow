import payments.nowpayments_api as api
from django.conf import settings
from users.models import User
from django.urls import reverse
import traceback


class PaymentServiceInfoProvider:

    @classmethod
    def get_min_payment_amount(cls):
        return settings.PAYMENT_MIN_AMOUNT


class TopupProcessor:

    class InvalidAmountError(Exception):
        pass

    class PaymentServiceInteractionError(Exception):
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
                callback_url=reverse("topup"),
                success_url=reverse("topup"),
                cancel_url=reverse("topup")
            )

            return invoice.invoice_url
        except Exception as e:
            traceback.print_exc()
            raise cls.PaymentServiceInteractionError from e

