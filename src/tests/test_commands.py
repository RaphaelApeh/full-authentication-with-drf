import io
from django.test import TestCase, override_settings
from django.core.management import call_command

from social_account.models import SocialProvider


class TestCommandTestCase(TestCase):

    @override_settings(
            SOCIAL_PROVIDER={
                "example": {}
            }
    )
    def test_command_create_provider(self):
        self.assertEqual(SocialProvider.objects.count(), 0)
        call_command(
            "create_provider", 
            "example",
            client_id="someclientid",
            secret_key="somesecretkey", 
            no_input=True
        )
        self.assertEqual(SocialProvider.objects.count(), 1)
        self.assertEqual(SocialProvider.objects.get().client_id, "someclientid")
    
    # def test_create_provider_dry_run(self):

    #     self.assertEqual(SocialProvider.objects.count(), 0)
        
    #     call_command(
    #         "create_provider", 
    #         "example2",
    #         client_id="someclientid2",
    #         secret_key="somesecretkey2",
    #         no_input=True,
    #         dry_run=True,
    #     )
    #     self.assertEqual(SocialProvider.objects.count(), 0)
        # self.assertIn("Dry run was added as a parameter.", output.getvalue())