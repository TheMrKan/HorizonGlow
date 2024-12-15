from rest_framework import serializers


class TopupSerializer(serializers.Serializer):
    amount = serializers.FloatField(write_only=True)


class NowpaymentsIPNSerializer(serializers.Serializer):
    invoice_id = serializers.CharField(write_only=True, allow_null=True)
    payment_status = serializers.CharField(write_only=True)
    price_amount = serializers.FloatField(write_only=True)
    order_id = serializers.CharField(write_only=True, allow_null=True)

