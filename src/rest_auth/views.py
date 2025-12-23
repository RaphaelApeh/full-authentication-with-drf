from django.contrib.auth import get_user_model, logout
from django.contrib.auth.tokens import default_token_generator
from rest_framework import status
from rest_framework.decorators import action
from rest_framework import permissions, authentication
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from social_account.serializers import SocialAccountSerializer
from .serializers import (
    UserRegistrationSerializer, UserSerializer, LoginSerializer, \
    ChangePasswordSerializer, EmailComfirmationSerializer,
    ForgotPasswordSerializer, PasswordResetSerializer
)

User = get_user_model()


class RegistrationView(APIView):

    serializer_class = UserRegistrationSerializer
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)
        

    def get_serializer(self, *args, **kwargs):
        return self.serializer_class(*args, context={'request': self.request}, **kwargs)
    

class LoginView(APIView):

    serializer_class = LoginSerializer
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status.HTTP_201_CREATED)

    def get_serializer(self, *args, **kwargs):
        serializer = self.serializer_class
        context = {"request": self.request}
        return serializer(*args, context=context, **kwargs)

class LogoutView(APIView):

    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        
        request.auth.delete()
        logout(request)
        return Response({"message": "Logedout successfully"})


class EmailConfirmationView(APIView):

    serializer_class = EmailComfirmationSerializer
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)
    

    def get_serializer(self, *args, **kwargs):
        context = {"request": self.request}
        return self.serializer_class(*args, context=context, **kwargs)


class UserViewSet(ModelViewSet):
    authentication_classes = [
        authentication.TokenAuthentication,
        authentication.SessionAuthentication,
    ]
    serializer_class = UserSerializer
    queryset = User.objects.select_related().order_by("-date_joined", "-last_login")
    pagination_class = PageNumberPagination


    def get_serializer_class(self):
        match self.action:
            case "change_password":
                self.serializer_class = ChangePasswordSerializer
            case "social_account" | "social_accounts":
                self.serializer_class = SocialAccountSerializer
            case "forgot_password":
                self.serializer_class = ForgotPasswordSerializer
        return super().get_serializer_class()


    @action(
            detail=False, 
            methods=["post"],
            permission_classes=[permissions.IsAuthenticated]
            )
    def change_password(self, request, *args, **kwargs):
        """
        Change current user password.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_200_OK)


    @action(
            detail=False, 
            permission_classes=[permissions.IsAuthenticated]
        )
    def me(self, request, *args, **kwargs):
        """
        Current authenticated user.
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status.HTTP_200_OK)

    @action(detail=False, methods=["GET"], permission_classes=[permissions.IsAuthenticated])
    def social_accounts(self, request, *args, **kwargs):
        socials = request.user.social_accounts.all()
        serializer = self.get_serializer(instance=socials, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @action(detail=True, methods=["GET"], permission_classes=[permissions.IsAuthenticated])
    def social_account(self, request, *args, **kwargs):
        if "provider" not in request.query_params:
            raise 
        provider = request.query_params["provider"]
        social = request.user.social_accounts.get(provider=provider)
        serializer = self.get_serializer(instance=social)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(
        detail=False, 
        methods=["POST"],
        url_name="forgot_password", 
        authentication_classes=[]
    )
    def forgot_password(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        match self.action:
            case "list":
                self.permission_classes = [
                    permissions.IsAdminUser
                ]
        return super().get_permissions()


class PasswordResetView(APIView):

    serializer_class = PasswordResetSerializer

    def post(self, request, *args, **kwargs):
        token = kwargs["token"]
        user_pk = kwargs["user_pk"]
        if not self.check_token(user_pk, token):
            raise NotFound()
        data = request.data.copy()
        data["user_pk"] = user_pk
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_204_NO_CONTENT)


    def check_token(self, user_pk, token):
        pk = User._meta.pk.to_python(user_pk)
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return False
        return default_token_generator.check_token(user, token)

    def get_serializer(self, *args, **kwargs):
        context = {"request": self.request, "view": self}
        return self.serializer_class(*args, context=context, **kwargs)



login_view = LoginView.as_view()
logout_view = LogoutView.as_view()
email_confirmation_view = EmailConfirmationView.as_view()
registration_view = RegistrationView.as_view()