import os.path
from django.db import models


class Article(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField("Title", max_length=100)
    content = models.TextField("Content")
    created_at = models.DateTimeField("Created at", auto_now_add=True)

    def get_image_path(self, filename):
        name, extension = os.path.splitext(filename)
        return f"article_images/{self.created_at.strftime('%Y%m%d%H%M%S')}{extension}"

    image = models.ImageField("Attached image", upload_to=get_image_path, null=True, default=None, blank=True)

    class Meta:
        verbose_name = "Article"
        indexes = [models.Index(fields=["-created_at"])]

    def __str__(self):
        return self.title

    def __repr__(self):
        return self.__str__()