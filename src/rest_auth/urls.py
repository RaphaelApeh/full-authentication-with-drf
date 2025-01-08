from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.registration_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("user/", views.user_view, name="user"),
    path("change-password/", views.change_password_view, name="change-password"),
    path("confirm-email/<int:user_pk>/<str:token>/", views.email_confirmation_view)
]