from rest_framework import serializers
from django.contrib.auth import authenticate

from users.services import UserCreator


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


class UserCredentialsSerializer(serializers.Serializer):
    username = serializers.CharField(
        label="Username",
        write_only=True
    )
    password = serializers.CharField(
        label="Password",
        style={'input_type': 'password'},
        trim_whitespace=False,
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

    def validate_username(self, value):
        if UserCreator(value, "", "").is_user_exists():
            raise serializers.ValidationError(f"User with this name already exists")

    def create(self, validated_data):
        try:
            user = UserCreator(validated_data["username"], validated_data["password"], validated_data["secret_phrase"]).create()
            return user
        except ValueError as e:
            raise serializers.ValidationError(str(e), code="authorization")



