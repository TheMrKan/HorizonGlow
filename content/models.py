from django.db import models


class ContentModel(models.Model):
    key = models.CharField(max_length=255, unique=True, primary_key=True)
    value = models.TextField()

    class Meta:
        verbose_name = 'Content'

    def __str__(self):
        return self.key

    def __repr__(self):
        return self.__str__()