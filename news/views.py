from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import Article
from .serializers import ArticleSerializer


class NewsViewSet(ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated, )
    model = Article
    serializer_class = ArticleSerializer
    queryset = Article.objects.order_by('-created_at').all()[:10]


