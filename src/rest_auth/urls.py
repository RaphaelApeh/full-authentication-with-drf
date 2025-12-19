from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register(r"users", views.UserViewSet, basename="user")

urlpatterns = [
    path("register/", views.registration_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path(
        "password-reset/<user_pk>/<token>/", 
        views.PasswordResetView.as_view(),
        name="password_reset"
    )
] + router.urls