from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import APIException


class OauthException(APIException):

    status_code = 400
    default_detail = _("Provider Error.")
    default_code = "provider_error"