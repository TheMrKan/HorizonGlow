from knox.auth import TokenAuthentication
from django.utils import timezone
from rest_framework.exceptions import AuthenticationFailed
from knox.models import get_token_model
from django.contrib.auth.signals import user_logged_in
from HorizonGlow.settings import REST_KNOX as custom_knox_settings
from knox.settings import knox_settings
from django.http import HttpResponse


class CookieTokenAuthentication(TokenAuthentication):
    def authenticate_through_cookie(self, request):
        prefix = self.get_cookie_key()
        if prefix in request.COOKIES:
            auth = request.get_signed_cookie(prefix, False, salt=self.get_cookie_salt())
            if not auth or len(auth) == 0:
                msg = 'Failed to get token value from cookies'
                return None
            user, auth_token = self.authenticate_credentials(auth.encode())
            return user, auth_token
        else:
            msg = 'No credentials provided through cookies'
            return None

    def authenticate(self, request):
        if self.get_cookie_auth_status():
            return self.authenticate_through_cookie(request)

        super().authenticate(request)

    @staticmethod
    def get_cookie_auth_status():
        return custom_knox_settings.get("ENABLE_COOKIE_AUTH", False)

    @staticmethod
    def get_cookie_salt():
        return custom_knox_settings.get("AUTH_COOKIE_SALT", "knox")

    @staticmethod
    def get_cookie_key():
        return custom_knox_settings.get("AUTH_COOKIE_KEY", "Token")

    @classmethod
    def create_token(cls, user):
        return get_token_model().objects.create(
            user=user, expiry=knox_settings.TOKEN_TTL, prefix=knox_settings.TOKEN_PREFIX
        )

    @classmethod
    def set_authentication_cookie(cls, response: HttpResponse, user):
        instance, token = cls.create_token(user)
        response.set_signed_cookie(cls.get_cookie_key(), token, httponly=True, salt=cls.get_cookie_salt(), max_age=knox_settings.TOKEN_TTL)

    @classmethod
    def remove_authentication_cookie(cls, response: HttpResponse):
        response.delete_cookie(cls.get_cookie_key())


