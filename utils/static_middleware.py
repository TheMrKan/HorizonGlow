from whitenoise.middleware import WhiteNoiseMiddleware
from django.conf import settings


class StaticMiddleware(WhiteNoiseMiddleware):
    def __call__(self, request):
        path = request.path_info
        if request.path_info == "/":
            path = settings.STATIC_URL + "index.html"
        elif not path.startswith(settings.STATIC_URL):
            path = settings.STATIC_URL + path.strip("/") + ".html"

        if self.autorefresh:
            static_file = self.find_file(path)
        else:
            static_file = self.files.get(path)
        if static_file is not None:
            return self.serve(static_file, request)
        return self.get_response(request)
