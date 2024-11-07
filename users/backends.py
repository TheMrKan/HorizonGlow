from django.contrib.auth.backends import ModelBackend
from .models import User
from .services import UserCredentialsManager


class SecretPhraseAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, secret_phrase=None):
        if None in (username, password):
            return None

        try:
            user = User.objects.get_by_natural_key(username)
        except User.DoesNotExist:
            return None
        else:
            pass

        if UserCredentialsManager(user, password, secret_phrase).check_credentials():
            return user

        return None



