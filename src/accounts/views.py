from django.views.generic import TemplateView


class LoginView(TemplateView):

    template_name = "login.html"


class SignUpView(TemplateView):

    template_name = "sign_up.html"


login_view = LoginView.as_view()
sign_up_view = SignUpView.as_view()