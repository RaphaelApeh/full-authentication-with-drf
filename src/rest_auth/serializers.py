from django.db import transaction
from django.contrib.auth import get_user_model, authenticate, \
      login
from django.contrib.auth.models import update_last_login

from rest_framework import serializers
from rest_framework.authtoken.models import Token

from .exceptions import UserFieldNotSet

User = get_user_model()


class PasswordField(serializers.CharField):

    def __init__(self, **kwargs):
        style = kwargs.get("style", {})
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
        username = attrs.get(_username)
        password = attrs.pop("password")
        if None in (username, password):
            raise UserFieldNotSet()
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

    password2 = serializers.CharField(style={'input_type':'password'})
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError("Password not Match.")
        if User.objects.filter(email__iexact=attrs['email']).exists():
            raise serializers.ValidationError("Email already exists.")
        return super().validate(attrs)

    def create(self, validated_data):
        password = validated_data.pop("password")
        validated_data.pop("password2")
        return User.objects.create_user(password=password, **validated_data)

    
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