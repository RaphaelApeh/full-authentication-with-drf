from django.contrib.auth import get_user_model
from django.db import transaction

from rest_framework import serializers

User = get_user_model()

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