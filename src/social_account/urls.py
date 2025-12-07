from django.urls import path

from .views.github import GithubOauthCallbackView, GithubLoginAPIView


urlpatterns = [

    # GitHub
    path("github/login/", GithubLoginAPIView.as_view(), name="github_login"),
    path("github/login/callback/", GithubOauthCallbackView.as_view(), name="github_callback")
]