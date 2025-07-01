from django.http import FileResponse
from rest_framework.decorators import action
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Article
from .serializers import ArticleSerializer
from utils.exceptions import APIException


class NewsViewSet(ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated, )
    model = Article
    serializer_class = ArticleSerializer
    queryset = Article.objects.order_by('-created_at').all()[:10]

    @action(detail=True,
            methods=["GET"],
            queryset=Article.objects.all())
    def image(self, request, pk=None):
        article: Article = self.get_object()

        if not article.image or not article.image.storage.exists(article.image.name):
            raise APIException(detail="This article doesn't have an image", code="no_file", status=status.HTTP_404_NOT_FOUND)

        file_handle = article.image.open()

        response = FileResponse(file_handle, content_type='whatever')
        response['Content-Length'] = article.image.size

        response['Content-Disposition'] = f'attachment; filename="{article.image.name}"'

        return response