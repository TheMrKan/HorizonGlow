from rest_framework import serializers
from django.contrib.auth import authenticate


class AuthTokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        label="Username",
        write_only=True
    )

    password = serializers.CharField(
        label="Password",
        style={'input_type': 'password'},
        write_only=True
    )

    secret_phrase = serializers.CharField(
        label="Secret Phrase",
        style={'input_type': 'password'},
        write_only=True
    )

    token = serializers.CharField(
        label="Token",
        read_only=True
    )

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")
        secret_phrase = attrs.get("secret_phrase")

        if username and password and secret_phrase:
            user = authenticate(request=self.context.get("request"),
                                username=username,
                                password=password,
                                secret_phrase=secret_phrase)

            if not user:
                msg = "Invalid credentials"
                raise serializers.ValidationError(msg, code='authorization')
        else:
            return serializers.ValidationError("Must include 'username', 'password' and 'secret_phrase'",
                                               code='authorization')

        attrs['user'] = user
        return attrs
