from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import authenticate
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import (ObjectDoesNotExist,
                                    ValidationError)

from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token

from .models import EmailConfirmation
from .serializers import UserRegistrationSerializer, UserSerializer

User = get_user_model()

class RegistrationView(APIView):

    serializer_class = UserRegistrationSerializer

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({"Error": serializer.errors})
        email = serializer.validated_data.get("email")
        if email is None:
            return Response({'Error':"Invaild Email."})
        serializer.save()
        username = serializer.validated_data.get("username")
        user  = User.objects.filter(username=username).first()
        token = default_token_generator.make_token(user)
        url = "/api/confirm-email/"
        link_to_confirm = request.build_absolute_uri(f"{url}{user.pk}/{token}/")
        user.email_user("Email Comfirmation", f"Dear {user.username}, Verify your email:{link_to_confirm}")

        
        return Response({'message': "A verification email has been sent to you."})
        

    def get_serializer(self, *args, **kwargs):
        return self.serializer_class(*args, context={'request', self.request}, **kwargs)
    

class LoginView(APIView):


    def post(self, request, *args, **kwargs):
        credentials = {
            "username" : request.data.get("username"),
            "password" : request.data.get("password")
        }
        try:
            user = authenticate(request, **credentials)
            if user is not None:
                if user.is_active:
                    token, _ = Token.objects.get_or_create(user=user)
                
                    return Response({"token": token.key})
            return Response({"Error": "Invalid data."})
        except Exception as e:
            return Response({"Error": f"Invalid data {e}."})


class LogoutView(APIView):

    authentication_classes = [TokenAuthentication]
    
    def post(self, request, *args, **kwargs):
        try:
            request.auth.delete()
            return Response({"message": "Logedout successfully"})
        except:
            return Response({"Error": "Invalid data."})
        

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
        except:

            return Response({"Error": "User does not exists."})


class ChangePasswordView(APIView):

    authentication_classes = [TokenAuthentication]

    def post(self, request, *args, **kwargs):
        
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        confrim_password = request.data.get("confrim_password")
        
        try:
            validate_password(new_password)
        except ValidationError as e:
    
            return Response({"Error": f" ".join(e)})    

        if new_password != confrim_password:
            return Response({"Error": "password not match."})

        if not all([old_password, new_password]):
            return Response({"Error": "An error occurred."})
        
        user = request.user
        if user.check_password(old_password):
            user.set_password(new_password)
            user.save()
            return Response({"message": "Password set successfully."})
        return Response({"Error": "Something went wrong."})


class UserView(APIView):
    authentication_classes = [TokenAuthentication]
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):

        user = request.user
        serializer = self.get_serializer(user, many=False)

        return Response(serializer.data)


    def post(self, request, *args, **kwargs):
        """
        update user credentials
        """
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


    def get_serializer(self, *args, **kwargs):

        return self.serializer_class(*args, context={'request': self.request}, **kwargs)


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
            url = "/api/new-password/"
            host_url = request.build_absolute_uri(f"{url}{user.pk}/{token}/")
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


class AllUsersView(APIView):

    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):

        query = request.query_params.get("q")
        qs = User.objects.all()
        if query:
            qs = qs.filter(username__icontains=query)[:15]

        serializer = self.get_serializer(qs, many=True)

        return Response(serializer.data)

    def get_serializer(self, *args, **kwargs):

        return self.serializer_class(*args, context={'request', self.request}, **kwargs)


login_view = LoginView.as_view()
logout_view = LogoutView.as_view()
user_view = UserView.as_view()
all_users_view = AllUsersView.as_view()
forgot_password_view = ForgotPasswordView.as_view()
change_password_view = ChangePasswordView.as_view()
change_forgot_password_view = ChangeForgotPasswordView.as_view()
email_confirmation_view = EmailConfirmationView.as_view()
registration_view = RegistrationView.as_view()