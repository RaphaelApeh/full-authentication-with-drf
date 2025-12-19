import pytest
from django.urls import reverse
from django.test import TestCase
from django.utils.lorem_ipsum import words
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


django_db = pytest.mark.django_db

User = get_user_model()


class TestAuth(TestCase):

    def setUp(self):
        super().setUp()
        self.client = APIClient()

        self.user = User.objects.create_user(
            username="testuser", 
            password="testpass",
            email="testuser@test.com"
        )
    
    @pytest.mark.skip
    def test_login_view(self):
        data = {"username": "testuser", "password": "testpass"}
        
        response = self.client.post(
            reverse("login"), 
            data=data,
        )
        print(response.data)
        assert response.status_code == 201 # create

    def test_register_view(self):
        data = {
            "username": "johndoe", 
            "email": "test@test.com",
            "password": "mdkxmfk", 
            "password2": "mdkxmfk",
        }
        response = self.client.post(
            reverse("register"),
            data=data,
            format="json"
        )
        assert response.status_code == 201
        user = User.objects.get(email=data["email"])
        self.client.force_authenticate(user)
        response = self.client.get(reverse("user-me"))
        assert response.status_code == 200

    def test_forgot_password_view(self):
        data = {"email": "testuser@test.com"}
        response = self.client.post(
            reverse("user-forgot_password"),
            data=data,
            format="json"
        )
        assert response.status_code == 204


    def test_change_password_view(self):
        password = words(8)
        data = {
            "old_password": "testpass",
            "new_password": password,
            "comfirm_password": password
        }
        user = self.user
        self.client.force_authenticate(user)
        response = self.client.post(
            reverse("user-change-password"),
            data=data,
            format="json"
        )
        response.status_code == 200
        user.refresh_from_db()
        self.assertIsNone(response.data) # no errors
        assert user.check_password(data["new_password"])
