from django.contrib.auth import login

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.mixins import ListModelMixin
from .serializers import AuthTokenSerializer, UserCredentialsSerializer, AccountSerializer
from .models import User
from .auth import CookieTokenAuthentication
from knox.views import LoginView as KnoxLoginView
from rest_framework.settings import api_settings
from .serializers import PurchaseSerializer


class RegisterView(KnoxLoginView):
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = UserCredentialsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        response = Response(data={}, status=status.HTTP_200_OK)
        CookieTokenAuthentication.set_authentication_cookie(response, user)
        return response


# часть кода из https://github.com/jazzband/django-rest-knox/pull/277
class LoginView(APIView):
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        response = Response(data={}, status=status.HTTP_200_OK)
        CookieTokenAuthentication.set_authentication_cookie(response, user)
        return response


class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        request._auth.delete()
        response = Response(data={}, status=status.HTTP_204_NO_CONTENT)
        CookieTokenAuthentication.remove_authentication_cookie(response)
        return response


class AccountView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        serializer = AccountSerializer(request.user)
        return Response(serializer.data)


class PurchasesView(ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PurchaseSerializer

    def get_queryset(self):
        return self.request.user.purchased_products.all()


