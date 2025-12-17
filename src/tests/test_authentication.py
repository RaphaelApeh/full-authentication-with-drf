import pytest

from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model


django_db = pytest.mark.django_db

User = get_user_model()


class TestAuth(TestCase):

    def setUp(self):
        super().setUp()
    
    def test_login_view(self):
        User.objects.all().delete()
        User.objects.create_user(username="testuser", password="testpass")
        data = {"username": "testuser", "password": "testpass"}
        response = self.client.post(reverse("login"), data=data)

        assert response.status_code == 201 # create

    def test_register_view(self):
        data = {
            "username": "johndoe", 
            "email": "test@test.com",
            "password1": "mdkxmfk", 
            "password2": "mdkxmfk",
        }
        response = self.client.post(reverse("register"), data)
        assert response.status_code == 201