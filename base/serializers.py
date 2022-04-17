from rest_framework.generics import get_object_or_404
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import Account


class AccountSerializer(ModelSerializer):
    password = serializers.CharField(max_length=1000, write_only=True)

    class Meta:
        model = Account
        fields = ('id', 'username', 'password', 'is_employee', 'is_restaurant_owner')

    def create(self, validated_data):
        return Account.objects.create_user(**validated_data)
