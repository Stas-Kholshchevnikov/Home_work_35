from rest_framework import serializers
from rest_framework.exceptions import ValidationError, NotAuthenticated
from django.contrib.auth.hashers import make_password

from Home_work_33.fields import PasswordField
from core.models import User


class CreateUserSerializers(serializers.ModelSerializer):
    password = PasswordField()
    password_repeat = PasswordField()

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'password', 'password_repeat')

    def validate(self, attrs: dict) -> dict:
        if attrs['password'] != attrs['password_repeat']:
            raise ValidationError('Passwords must match')
        return attrs

    def create(self, validated_data: dict) -> User:
        del validated_data['password_repeat']
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


class LoginSerializers(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = PasswordField(validate=False)


class ProfileSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')


class UpdatePasswordSerializers(serializers.Serializer):
    old_password = PasswordField(validate=False)
    new_password = PasswordField()

    def validate_old_password(self, old_password: str) -> str:
        request = self.context['request']
        if not request.user.is_authenticated:
            raise NotAuthenticated
        if not request.user.check_password(old_password):
            raise ValidationError('Old password is not correct')
        return old_password
