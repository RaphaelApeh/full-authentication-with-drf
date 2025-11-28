import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture(autouse=True)
def user():
    user = User.objects.create_user("testuser", password="testpassword")
    return user

@pytest.fixture
def token_qs():
    return Token.objects.all()