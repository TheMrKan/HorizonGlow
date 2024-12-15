from rest_framework import serializers


class TopupSerializer(serializers.Serializer):
    amount = serializers.FloatField(write_only=True)
