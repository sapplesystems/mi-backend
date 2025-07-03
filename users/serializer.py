from rest_framework import serializers
from users.models import User


class AddUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'user_role', 'is_active']
