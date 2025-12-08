from django.contrib import admin

from .models import SocialProvider, SocialAccount


@admin.register(SocialProvider)
class SocialProviderAdmin(admin.ModelAdmin):
    search_fields = "provider"


@admin.register(SocialAccount)
class SocialAccountAdmin(admin.ModelAdmin):
    ...