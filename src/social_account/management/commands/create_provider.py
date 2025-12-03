from getpass import getpass

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from social_account.models import SocialProvider


class Command(BaseCommand):

    help = "Creates oauth provider"


    def add_arguments(self, parser):
        parser.add_argument(
            "provider", 
            help="Name of oauth provider",
            )
        parser.add_argument(
            "--no-input",
            "--noinput",
            action="store_true"
        )
        

    def handle(self, *args, **options):
        provider_data = dict()
        provider_name = options["provider"]
        if provider_name not in settings.SOCIAL_PROVIDER:
            raise CommandError(self.style.ERROR("Invalid provider %s" % provider_name))
        if SocialProvider.objects.filter(provider=provider_name).exists():
            raise CommandError(self.style.WARNING("Provider already exists."))
        provider_setting = settings.SOCIAL_PROVIDER[provider_name]
        client_id = provider_setting.get("CLIENT_ID", None)
        secret_key = provider_setting.get("SECRET_KEY", None)
        count = 0
        while not options["no_input"] and count < 3:
            client_id = getpass("Client ID: ")
            secret_key = getpass("Secret Key: ")
            if (client_id is None or client_id == "") or \
                (secret_key is None or secret_key == ""):
                self.stderr.write(
                    self.style.ERROR("Client ID or Secret Key is not provided")
                )
                count += 1
                continue
            elif client_id and secret_key:
                break
        if not client_id or not secret_key:
            if count == 3:
                msg = "Max count reached."
                self.stderr.write(self.style.WARNING(msg))
            raise CommandError(self.style.ERROR("Client ID or Secret Key is not provided"))
        else:
            provider_data["client_id"] = client_id
            provider_data["secret_key"] = secret_key
        
        if all(provider_data[d] for d in provider_data):
            provider = SocialProvider(
                provider=provider_name, 
                **provider_data
            )
            provider.save()
            
            return self.stderr.write(self.style.SUCCESS("Provider Saved."))
        raise CommandError("Error: something went wrong.")

    def print_error(self, text):
        self.stderr.write(self.style.ERROR(text))