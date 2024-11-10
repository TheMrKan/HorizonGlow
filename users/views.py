from django.contrib.auth import login

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import AuthTokenSerializer, UserCredentialsSerializer
from .models import User
from knox.views import LoginView as KnoxLoginView


class LoginView(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return super(LoginView, self).post(request, format=None)


class RegisterView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = UserCredentialsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

