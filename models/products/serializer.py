from rest_framework import serializers
from .models import Products


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = ['category', 'category_code', ]
