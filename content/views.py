from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from utils.exceptions import APIException
from .models import ContentModel


class ContentView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        name = request.query_params.get('name')
        if not name:
            raise APIException('Content name must be provided', code="name_not_provided", status=status.HTTP_400_BAD_REQUEST)

        try:
            content = ContentModel.objects.get(key=name)
        except ContentModel.DoesNotExist:
            raise APIException('Content not found', code="not_found", status=status.HTTP_404_NOT_FOUND)
        return Response(content.value)

