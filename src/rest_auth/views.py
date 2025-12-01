from django.urls import reverse
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.tokens import default_token_generator
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from rest_framework import status
from rest_framework.decorators import action
from rest_framework import permissions, authentication
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from .models import EmailConfirmation
from .serializers import UserRegistrationSerializer, UserSerializer, LoginSerializer, \
    ChangePasswordSerializer


User = get_user_model()


class RegistrationView(APIView):

    serializer_class = UserRegistrationSerializer

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)
        

    def get_serializer(self, *args, **kwargs):
        return self.serializer_class(*args, context={'request', self.request}, **kwargs)
    

class LoginView(APIView):

    serializer_class = LoginSerializer
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status.HTTP_201_CREATED)

    def get_serializer(self, *args, **kwargs):
        serializer = self.serializer_class
        context = {"request": self.request}
        return serializer(*args, context=context, **kwargs)

class LogoutView(APIView):

    authentication_classes = [
        authentication.TokenAuthentication, 
        authentication.SessionAuthentication
    ]
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        
        request.auth.delete()
        logout(request)
        return Response({"message": "Logedout successfully"})


class EmailConfirmationView(APIView):
    
    def post(self, request, *args, **kwargs):
        
        user_id = kwargs["user_pk"]
        token = kwargs["token"]

        try:
            user = User.objects.get(pk=user_id)
            if default_token_generator.check_token(user, token):
                _email = EmailConfirmation.objects.get(user=user)
                _email.is_confirmed = True
                _email.save()
                return Response({"message": f"Email {_email.email} is confirmed."})
        except Exception:

            return Response({"Error": "User does not exists."})


class UserViewSet(ModelViewSet):
    authentication_classes = [
        authentication.TokenAuthentication,
        authentication.SessionAuthentication,
    ]
    serializer_class = UserSerializer
    queryset = User.objects.select_related()

    def get_serializer_class(self):
        match self.action:
            case "change_password":
                self.serializer_class = ChangePasswordSerializer
        return super().get_serializer_class()


    @action(detail=False)
    def change_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


    @action(detail=False)
    def me(self, request, *args, **kwargs):
        """
        Current authenticated user.
        """
        serializer = self.get_serializer(self.get_object())
        return Response(serializer.data, status.HTTP_200_OK)

    def get_permissions(self):
        match self.action:
            case "me":
                self.permission_classes = permissions.IsAuthenticated
        return super().get_permissions()


class ForgotPasswordView(APIView):
    

    def post(self, request, *args, **kwargs):

        email  = request.data.get("email")
        if email is not None:
            try:
                validate_email(email)
            except ValidationError as e:
                return Response({"Error": " ".join(e)})
        qs = User.objects.filter(email__iexact=email)
        if qs.exists():
            user = qs.get()
            token = default_token_generator.make_token(user)
            url = reverse("change-forgot-password", args=(user.pk, token))
            host_url = request.build_absolute_uri(f"{url}")
            user.email_user("Forgot Password ?", f"Dear {user.username}, Link to change password {host_url} ")

            return Response({"message": "Email sent."})
        return Response({"Error": f"{email} does not exists."})


class ChangeForgotPasswordView(APIView):


    def post(self, request, *args, **kwargs):

        user_pk = kwargs["user_pk"]
        token = kwargs["token"]
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")
        
        qs = User.objects.filter(pk=user_pk)
        if not qs.exists():
            return Response({"error": "Invalid data."})
        try:
            validate_password(new_password)
        except ValidationError as e:
            return Response({"error": " ".join(e)})
        if new_password != confirm_password:
            return Response({'error': "Password not match.."})
        try:
            _user = qs.first()
        except (User.MultipleObjectsReturned, User.DoesNotExist):
            return Response({"error": "Error ..."})
        if default_token_generator.check_token(_user, token):
            _user.set_password(new_password)
            _user.save()
            return Response({"message": "password set successfully."})
        return Response({"error": "Something went wrong."})



login_view = LoginView.as_view()
logout_view = LogoutView.as_view()
forgot_password_view = ForgotPasswordView.as_view()
change_forgot_password_view = ChangeForgotPasswordView.as_view()
email_confirmation_view = EmailConfirmationView.as_view()
registration_view = RegistrationView.as_view()