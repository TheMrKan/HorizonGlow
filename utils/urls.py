import urllib.parse
from django.conf import settings


def get_absolute_url(relative: str, protocol: str = "https"):
    return urllib.parse.urljoin(f"{protocol}://{settings.HOSTNAME}", relative)