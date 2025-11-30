from django.db import transaction
from django.urls import reverse
from django.contrib.auth import get_user_model, authenticate, \
      login
from django.contrib.auth.models import update_last_login
from django.contrib.auth.tokens import default_token_generator

from rest_framework import serializers
from rest_framework.authtoken.models import Token


User = get_user_model()


class PasswordField(serializers.CharField):

    def __init__(self, **kwargs):
        style = kwargs.setdefault("style", {})
        style["input_type"] = "password"
        kwargs["write_only"] = True
        super().__init__(**kwargs)


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
        for key, value in credentials.items():
            if User.objects.filter(**{f"{key}__iexact": value}).exists():
                raise serializers.ValidationError(f"{key.upper()} already exists.")
        
        return {
            "email": email,
            "message": "Account veritication code sent."
        }
    
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

    
class UserSerializer(serializers.ModelSerializer):

    full_name = serializers.CharField(source="get_full_name", read_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "full_name"]
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