from rest_framework.exceptions import APIException


class UserFieldNotSet(APIException):

    status_code = 403
