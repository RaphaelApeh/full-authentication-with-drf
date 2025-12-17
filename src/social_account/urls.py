from django.urls import path

from .views import DisconnectSocialAPIView
from .views.github import GithubOauthCallbackView, GithubLoginAPIView


urlpatterns = [

    path("disconnect/<int:social_id>/", DisconnectSocialAPIView.as_view(), name="disconnect_social"),

    # GitHub
    path("github/login/", GithubLoginAPIView.as_view(), name="github_login"),
    path("github/login/callback/", GithubOauthCallbackView.as_view(), name="github_callback")
]