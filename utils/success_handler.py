from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def return_code(request, code: int):
    response = HttpResponse()
    response.status_code = code
    return response
