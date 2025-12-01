from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register(r"users", views.UserViewSet, basename="user")

urlpatterns = [
    path("register/", views.registration_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("forgot-password/", views.forgot_password_view, name="forgot-password"),
    path("new-password/<int:user_pk>/<str:token>/", views.change_forgot_password_view, name="change-forgot-password"),
    path("confirm-email/<int:user_pk>/<str:token>/", views.email_confirmation_view)
] + router.urls