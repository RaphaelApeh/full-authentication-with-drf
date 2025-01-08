from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import (ObjectDoesNotExist,
                                    ValidationError)

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
            return Response({"Error": f"Invaild data {serializer.errors}."})
        email = serializer.validated_data.get("email")
        if email is None:
            return Response({'Error':"Invaild Email."})
        serializer.save()
        username = serializer.validated_data.get("username")
        user  = User.objects.filter(username=username).first()
        token = default_token_generator.make_token(user)
        link_to_confirm = request.build_absolute_uri(f"/api/confirm-email/{user.pk}/{token}/")
        user.email_user("Email Comfirmation", f"Verify email:{link_to_confirm}")

        
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
            if user.is_active:
                token, _ = Token.objects.get_or_create(user=user)
            
                return Response({"token": token.key})
            return Response({"Error": "User is not verifed."})
        except Exception as e:
            return Response({"Error": f"Invalid data {e}."})


class LogoutView(APIView):

    authentication_classes = [TokenAuthentication]
    
    def post(self, request, *args, **kwargs):
        try:
            request.auth.delete()
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
                return Response({"message": "User is verifed."})
        
        except ObjectDoesNotExist:

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
            return Response({"message": "Password set successfuly."})
        return Response({"Error": "Something went wrong."})


class UserView(APIView):
    authentication_classes = [TokenAuthentication]

    def get(self, request, *args, **kwargs):

        user = request.user
        serializer = UserSerializer(user, many=False)

        return Response(serializer.data)

class ForgotPasswordView(APIView):
    ...



login_view = LoginView.as_view()
logout_view = LogoutView.as_view()
user_view = UserView.as_view()
change_password_view = ChangePasswordView.as_view()
email_confirmation_view = EmailConfirmationView.as_view()
registration_view = RegistrationView.as_view()