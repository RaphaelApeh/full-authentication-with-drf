from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailConfirmation(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    email = models.EmailField(unique=True)
    is_confirmed = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)


    def save(self, *args, **kwargs):
        if self.user is not None:
            if self.is_confirmed:
                self.user.is_active = True
                self.user.save()
        super().save()


    def __str__(self):
        return self.user.username if self.user is not None else self.email