from django.contrib import admin

from .models import EmailConfirmation

@admin.register(EmailConfirmation)
class EmailAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_confirmed', 'sent_at']