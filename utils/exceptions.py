from rest_framework.exceptions import APIException as _APIException


class APIException(_APIException):

    def __init__(self, *args, status: int = 500, **kwargs):
        super().__init__(*args, **kwargs)
        self.status_code = status
