from django.contrib.auth import get_user_model

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

    def update(self, instance, validated_data):

        instance = super().update(instance, validated_data)

        instance.username = validated_data.get("username", instance.username)
        instance.email = validated_data.get("email", instance.email)
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.save()

        return instance