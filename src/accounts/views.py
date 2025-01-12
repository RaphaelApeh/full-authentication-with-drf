from django.views.generic import TemplateView


class LoginView(TemplateView):
    
    template_name = "login.html"


class SignUpView(TemplateView):

    template_name = "sign_up.html"


class LogoutView(TemplateView):

    template_name = "log_out.html"


class HomePageView(TemplateView):

    template_name = "home_page.html"


home_page_view = HomePageView.as_view()
login_view = LoginView.as_view()
logout_view = LogoutView.as_view()
sign_up_view = SignUpView.as_view()