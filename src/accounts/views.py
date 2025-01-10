from django.views.generic import TemplateView


class LoginView(TemplateView):

    template_name = "login.html"


class SignUpView(TemplateView):

    template_name = "sign_up.html"