from rest_framework.serializers import ModelSerializer
from .models import Article


class ArticleSerializer(ModelSerializer):

    class Meta:
        model = Article
        fields = ("id", "title", "content", "created_at")
