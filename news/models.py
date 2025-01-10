from django.db import models


class Article(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField("Title", max_length=100)
    content = models.TextField("Content")
    created_at = models.DateTimeField("Created at", auto_now_add=True)

    class Meta:
        verbose_name = "Article"
        indexes = [models.Index(fields=["-created_at"])]

    def __str__(self):
        return self.title

    def __repr__(self):
        return self.__str__()