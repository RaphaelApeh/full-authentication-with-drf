from django.urls import path

from . import views

urlpatterns = [
    path("", views.home_page_view),
    path("signup/", views.sign_up_view),
    path("logout/", views.logout_view),
    path("login/", views.login_view)
]