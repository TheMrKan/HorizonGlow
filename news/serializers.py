from rest_framework.serializers import ModelSerializer, SerializerMethodField
from .models import Article


class ArticleSerializer(ModelSerializer):
    has_image = SerializerMethodField()

    class Meta:
        model = Article
        fields = ("id", "title", "category", "content", "created_at", "has_image")

    def get_has_image(self, instance: Article):
        return bool(instance.image) and instance.image.storage.exists(instance.image.name)
