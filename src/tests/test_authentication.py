import pytest

from django.urls import reverse

django_db = pytest.mark.django_db


class TestAuth:
    
    @django_db
    def test_login_view(self, api_client, user, token_qs):
        data = {"user": "testuser", "password": "testpass"}
        response = api_client.post(reverse("login"), data=data)

        assert response.status_code == 201 # create
        assert response.data["message"] == "Login successfully."
        token = response.data["token"]
        assert token_qs.filter(token=token).exists()

    @django_db
    def test_register_view(self, api_client):
        data = {
            "username": "johndoe", 
            "email": "test@test.com",
            "password1": "mdkxmfk", 
            "password2": "mdkxmfk",
        }
        response = api_client.post(reverse("register"), data)
        assert response.status_code == 201