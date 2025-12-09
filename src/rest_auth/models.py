import uuid

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.template import loader
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from .helpers import send_email


User = get_user_model()


class EmailConfirmation(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    email = models.EmailField(unique=True)
    token = models.CharField(max_length=100, default="")
    is_confirmed = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.token:
            self.token = str(uuid.uuid1())[:4]

    def save(self, *args, **kwargs):
        if user := self.user:
            if self.is_confirmed:
                user.is_active = True
                user.save()
        super().save()
        self.expire_token()

    def expire_token(self):
        if self.is_expired:
            self.delete()

    def check_token(self, request, token):
        return self.token == token

    @property
    def is_expired(self):
        expired_ = self.sent_at + timezone.timedelta(minutes=settings.EMAIL_COMFIRMATION_EXPIRATION)
        return expired_ <= timezone.now()

    def send(self, request, template_name=None):
        email = self.email
        if not email:
            email = self.user.email
        temp = loader.get_template(template_name or "email.txt")
        subject = _("Email Comfirmation Code")
        saved = not self._state.adding
        context = {"object": self, "saved": saved}
        send_email(subject, [email], temp.render(context))


    def __str__(self):
        return self.user.username if self.user is not None else self.email