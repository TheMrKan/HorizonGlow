from django.db.transaction import commit
from rest_framework import serializers, status
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.urls import reverse
from .models import User
from products.models import Product
from products.services import ProductFileManager
from users.services import UserCreator, UserCredentialsManager


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
                raise AuthenticationFailed()
        else:
            return serializers.ValidationError("Must include 'username', 'password' and 'secret_phrase'",
                                               code=status.HTTP_400_BAD_REQUEST)

        attrs['user'] = user
        return attrs


def _validate_secret_phrase(secret_phrase):
    if len(secret_phrase) < 3 or len(secret_phrase) > 15:
        raise serializers.ValidationError(
            "Secret phrase must be at least 3 characters long and less than 15 characters")

    if not secret_phrase.isalpha():
        raise serializers.ValidationError("Secret phrase must contain only alphabetic characters")
    return secret_phrase


class UserCredentialsSerializer(serializers.Serializer):
    username = serializers.CharField(
        label="Username",
        write_only=True,
    )
    password = serializers.CharField(
        label="Password",
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True,
        validators=[validate_password]
    )
    secret_phrase = serializers.CharField(
        label="Secret Phrase",
        style={'input_type': 'password'},
        write_only=True,
        validators=[_validate_secret_phrase]
    )
    token = serializers.CharField(
        label="Token",
        read_only=True
    )

    def validate_username(self, value):
        if len(value) < 4:
            raise serializers.ValidationError("Username must be at least 4 characters long")

        if UserCreator(value, "", "").is_user_exists():
            raise serializers.ValidationError(f"User with this name already exists")
        return value

    def create(self, validated_data):
        try:
            user = UserCreator(validated_data["username"], validated_data["password"], validated_data["secret_phrase"]).create()
            return user
        except ValueError as e:
            raise serializers.ValidationError(str(e), code="authorization")


class AccountSerializer(serializers.ModelSerializer):
    password_new = serializers.CharField(label="New password", write_only=True, validators=[validate_password])
    secret_phrase_new = serializers.CharField(label="Secret Phrase", write_only=True, validators=[_validate_secret_phrase])

    class Meta:
        model = User
        fields = ('username', 'balance', 'password', 'password_new', 'secret_phrase', 'secret_phrase_new')
        write_only_fields = ('password', 'secret_phrase')

    def validate(self, attrs):
        password = attrs.get("password")
        secret_phrase = attrs.get("secret_phrase")
        password_valid, phrase_valid = UserCredentialsManager(self.instance, password, secret_phrase).check_credentials_partial()
        detail = {}
        if not password_valid:
            detail["password"] = "Incorrect password"
        if not phrase_valid:
            detail["secret_phrase"] = "Incorrect secret phrase"

        if detail:
            raise serializers.ValidationError(detail, code="incorrect_current")

        return attrs

    def update(self, instance, validated_data):
        UserCredentialsManager(instance, validated_data.get("password_new"), validated_data.get("secret_phrase_new")).update_credentials(commit=True, partial=True)
        return instance


class PurchaseSerializer(serializers.ModelSerializer):
    file_available = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()

    def get_file_available(self, obj: Product):
        return ProductFileManager(obj).has_file()

    def get_file_url(self, obj: Product):
        return reverse("product-download", kwargs={"pk": obj.id})

    class Meta:
        model = Product
        fields = ('id', 'description', 'number', 'score', 'purchased_at', 'price', "file_available", "file_url")



