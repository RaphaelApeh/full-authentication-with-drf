from django.db import transaction
from django.urls import reverse
from django.template import loader
from django.contrib.auth import get_user_model, authenticate, \
      login
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import update_last_login
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from .helpers import send_email
from .models import EmailConfirmation


User = get_user_model()


class PasswordField(serializers.CharField):

    def __init__(self, **kwargs):
        style = kwargs.setdefault("style", {})
        style["input_type"] = "password"
        kwargs["write_only"] = True
        super().__init__(**kwargs)


class UserEmailMixin:

    template_name = None

    def get_template(self, context):
        temp = loader.get_template(self.template_name)
        return temp.render(context)

    def send(self, request, to, subject, body=None, context=None):
        if not body:
            body = self.get_template({"user": request.user, "to": to, **{context or {}}})
        send_email(subject, to, body)


class LoginSerializer(serializers.Serializer):

    password = PasswordField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[User.USERNAME_FIELD] = serializers.CharField()

    def validate(self, attrs):
        credentials = {}
        _username = User.USERNAME_FIELD
        username = attrs.pop(_username)
        password = attrs.pop("password")
        credentials[_username] = username
        credentials["password"] = password
        request = self.context.get("request")
        user = authenticate(request, **credentials)
        if not user:
            raise serializers.ValidationError("Invalid %s or password field." % _username)
        login(request, user)
        update_last_login(None, user)
        token, _ = Token.objects.get_or_create(user=user)
        attrs = {
            "message": "Login successfully.",
            "token": token.key
        }
        return super().validate(attrs)
    

class UserRegistrationSerializer(serializers.ModelSerializer):

    password2 = PasswordField()
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']

    def validate(self, attrs):
        credentials = {}
        username = attrs.pop("username")
        email = attrs.pop("email")
        credentials["username"] = username
        password = attrs.get("password")
        password2 = attrs.get("password2")
        if not password and not password2 or password != password2:
            raise serializers.ValidationError("Password not Match.")
        credentials["email"] = email
        fake_user = User(**credentials)
        fake_user.full_clean()
        return {
            "email": email,
            "message": "Account veritication code sent."
        }
    
    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            return value
        raise serializers.ValidationError("Invalid email or username.")
    
    def save(self, **kwargs):
        if (instance := self.instance) is None:
            self.instance = self.create(self.data)
        else:
            self.instance = self.update(instance, self.data)
        return self.instance

    def create(self, validated_data):
        password = validated_data.get("password")
        request = self.context.get("request")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        token = default_token_generator.make_token(user)
        url = reverse("change-forgot-password", args=(user.pk, token))
        link_to_confirm = request.build_absolute_uri(f"{url}")
        user.email_user("Account Veritication", f"Dear {user.username}, Verify your email:\n{link_to_confirm}")
        return user


class ChangePasswordSerializer(serializers.Serializer):

    old_password = PasswordField()
    new_password = PasswordField()
    comfirm_password = PasswordField()

    def validate(self, attrs):
        request = self.context.get("request")
        user = request.user
        old_password = attrs.get("old_password")
        new_password = attrs.get("new_password")
        comfirm_password = attrs.get("comfirm_password")
        if new_password or comfirm_password and new_password != comfirm_password:
            raise serializers.ValidationError("Password not Match.")
        try:
            validate_password(new_password)
        except ValidationError as e:
            raise serializers.ValidationError("\n".join(e.messages))
        if user.check_password(old_password):
            user.set_password(new_password)
            user.save()
        else:
            raise serializers.ValidationError("Invalid password.")
        return {
            "message": "Password change successfully."
        }


class ForgotPasswordSerializer(UserEmailMixin, serializers.Serializer):

    template_name = "forgot-password.txt"
    
    email = serializers.EmailField()

    def validate(self, attrs):
        email = attrs["email"]
        request = self.context.get("request")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            pass
        else:
            token = default_token_generator.make_token(user)
            url = request.build_absolute(
                reverse("change-forgot-password", args=(user.pk, token))
            )
            self.send(
                request,
                to=[email], 
                subject="Forgot Password",
                context={"url": url}
            )
        return super().validate(attrs)


class UserSerializer(serializers.ModelSerializer):

    full_name = serializers.CharField(source="get_full_name", read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "full_name", "is_active"]
        extra_kwargs = {
            "username": {"required": False}
        }

    def update(self, instance, validated_data):

        instance = super().update(instance, validated_data)
        with transaction.atomic():
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

        return instance


class EmailComfirmationSerializer(serializers.Serializer):

    token = serializers.CharField(write_only=True)
    user_pk = serializers.CharField()


    def validate(self, attr):
        user_pk = attr["user_pk"]
        token = attr["token"]
        try:
            pk = User._meta.pk.to_python(user_pk)
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise serializers.ValidationError("User Id is invalid.")
        if not self.check_token(user, token):
            raise serializers.ValidationError("Invalid token.")
        _email = EmailConfirmation.objects.get(user=user)
        _email.is_confirmed = True
        _email.save()
        return {
            "message": "Email verified"
        }
    
    def check_token(self, user, token: str) -> bool:

        return default_token_generator.check_token(user, token)

