from django.test import TestCase as BaseTestCase


class TestCase(BaseTestCase):


    def assertStatusCode(self, response=None, expected_code=None, msg=None) -> None:

        if not response:
            self.fail("Expected a Response instance but got '%s'" % type(response))
        assert hasattr(response, "status_code")
        status_code = response.status_code
        if expected_code:
            self.assertEqual(status_code, expected_code, msg)
        
        if 400 <= status_code < 500:
            self.fail(msg or f"{status_code} Client Error.")
        elif 500 <= status_code < 600:
            self.fail(msg or f"{status_code} Server Error.")
        

