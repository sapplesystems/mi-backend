from rest_framework import serializers
from .models import contactus


class CreateContactusSerializer(serializers.ModelSerializer):
    class Meta:
        model = contactus
        fields = '__all__'
