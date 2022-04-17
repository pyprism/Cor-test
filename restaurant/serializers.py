from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import Menu, Restaurant, MenuVote
from base.serializers import AccountSerializer


class RestaurantSerializer(ModelSerializer):

    class Meta:
        model = Restaurant
        fields = ('id', 'name')


class MenuSerializer(ModelSerializer):
    owner = RestaurantSerializer(read_only=True)

    class Meta:
        model = Menu
        fields = ('id', 'name', 'owner')


class VoteSerializer(ModelSerializer):
    menu = MenuSerializer(read_only=True)
    employee = AccountSerializer(read_only=True)
    menu_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = MenuVote
        fields = ('id', 'menu', 'employee', 'menu_id')

