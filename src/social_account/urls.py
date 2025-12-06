from django.urls import path

from .views.base import OauthLoginAPIView
from .views.github import GithubOauthCallbackAPIView

urlpatterns = [
    path("login/", OauthLoginAPIView.as_view(), name="social_login"),
    path("github/login/callback/", GithubOauthCallbackAPIView.as_view(), name="github_callback")
]