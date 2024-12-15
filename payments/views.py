import time

from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from utils.exceptions import APIException
from .services import PaymentServiceInfoProvider, TopupProcessor
from .serializers import TopupSerializer


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

