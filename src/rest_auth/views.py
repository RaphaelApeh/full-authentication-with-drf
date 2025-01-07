from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token

from .serializers import UserRegistrationSerializer
from .models import EmailConfirmation

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

class ForgotPasswordView(APIView):
    ...



login_view = LoginView.as_view()
logout_view = LogoutView.as_view()
email_confirmation_view = EmailConfirmationView.as_view()
registration_view = RegistrationView.as_view()