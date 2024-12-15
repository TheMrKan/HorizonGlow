import time
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import permissions, status
from utils.exceptions import APIException
from .services import PaymentServiceInfoProvider, TopupProcessor
from .serializers import TopupSerializer, NowpaymentsIPNSerializer
from payments.nowpayments_api import is_ipn_sig_valid
from django.conf import settings


class PaymentServiceInfo(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        return Response({"min_amount": PaymentServiceInfoProvider.get_min_payment_amount()})


class TopupView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = TopupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            url = TopupProcessor.request_topup(request.user, serializer.validated_data["amount"])
        except TopupProcessor.InvalidAmountError:
            raise ValidationError({"amount": "Invalid amount"}, code="invalid_amount")
        except TopupProcessor.PaymentServiceInteractionError:
            raise APIException("An error occured while interacting with the payment service. Please, try again.", code="payment_service_interaction", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"payment_url": url}, status=status.HTTP_201_CREATED)


class NowpaymentsIPNView(APIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def post(self, request: Request):
        if "x-nowpayments-sig" not in request.headers.keys():
            raise APIException("Signature is not provided", code="invalid_signature", status=status.HTTP_401_UNAUTHORIZED)

        request_sig = request.headers["x-nowpayments-sig"]
        if not is_ipn_sig_valid(settings.PAYMENT_SERVICE_IPN_KEY, request_sig, request.data):
            pass # raise APIException("Invalid signature", code="invalid_signature", status=status.HTTP_401_UNAUTHORIZED)

        serializer = NowpaymentsIPNSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            TopupProcessor.update_topup_status(serializer.validated_data["order_id"], serializer.validated_data["payment_status"], float(serializer.validated_data["price_amount"]))
        except TopupProcessor.InvalidOrderIdError:
            raise APIException("Invalid order ID", code="invalid_order_id", status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)




