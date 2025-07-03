from rest_framework import serializers
from models.verify_user.models import verify_user


class VerifyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = verify_user
        fields = '__all__'
