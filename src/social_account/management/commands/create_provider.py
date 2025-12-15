from getpass import getpass

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.core.exceptions import ValidationError

from social_account.models import SocialProvider


class Command(BaseCommand):

    help = "Creates oauth provider"

    def add_arguments(self, parser):
        parser.add_argument(
            "provider",
            metavar="Oauth2 Provider",
            nargs="?",
            help="Name of oauth2s provider",
            )
        parser.add_argument(
            "--no-input",
            "--noinput",
            action="store_true"
        )
        parser.add_argument(
            "--dry-run",
            "--dryrun",
            action="store_true"
        )
        

    def handle(self, *args, **options):
        provider_data = dict()
        provider_name = options["provider"]
        if provider_name not in settings.SOCIAL_PROVIDER:
            self.stderr.write(
                self.style.WARNING("No extra configuration in provider settings.")
            )
        if SocialProvider.objects.filter(provider=provider_name).exists():
            raise CommandError(self.style.WARNING("Provider already exists."))
        provider_setting = settings.SOCIAL_PROVIDER.get(provider_name, {})
        client_id = provider_setting.get("CLIENT_ID", "")
        secret_key = provider_setting.get("SECRET_KEY", "")
        count = 0
        while not options["no_input"] and count < 3:
            client_id = getpass("Client ID: ")
            secret_key = getpass("Secret Key: ")
            if not client_id and not secret_key:
                
                self.print_error("Client ID or Secret Key is not provided")
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
        
        provider = SocialProvider(
                provider=provider_name,
                **provider_data
            )
        try:
            provider.full_clean()
        except ValidationError as e:
            errors = "\n".join(
                [key + ": " + value for key, value in e.message_dict.items()]
            )
            raise CommandError("\nPlease correct the following errors:\n %s" % errors)
        if not options["dry_run"]:
            provider.save()            
            return self.stderr.write(self.style.SUCCESS("Provider Saved."))
        else:
            self.stderr.write(
                self.style.WARNING(
                    "%s provider was not saved."
                    "\nDry run was added as a parameter." % provider.provider
                )
            )
            
        raise CommandError("Error: something went wrong.")

    def print_error(self, text):
        self.stderr.write(self.style.ERROR(text))