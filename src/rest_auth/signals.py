from django.db.models.signals import post_save, pre_save
from django.contrib.auth import get_user_model
from django.utils import timezone


from .models import EmailConfirmation

def create_auth_token(sender, instance, created, **kwargs):
    if created:
        instance.last_login = timezone.now()
        instance.is_active = False
        EmailConfirmation.objects.create(user=instance, email=instance.email)
        instance.save()

post_save.connect(create_auth_token, sender=get_user_model())