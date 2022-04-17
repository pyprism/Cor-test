from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework import viewsets

from base.models import Account
from .serializers import RestaurantSerializer, MenuSerializer, VoteSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Restaurant, Menu, MenuVote, VoteResultTracker
from .utils import IsRestaurantOwner, MenuPermission, IsEmployee
from rest_framework.authentication import SessionAuthentication, BasicAuthentication


class RestaurantViewSet(ModelViewSet):
    serializer_class = RestaurantSerializer
    queryset = Restaurant.objects.get_restaurant_list()
    authentication_classes = [SessionAuthentication, BasicAuthentication, JWTAuthentication]
    permission_classes = [IsRestaurantOwner]

    def create(self, request, *args, **kwargs):
        input_data = RestaurantSerializer(data=request.data)
        if input_data.is_valid():
            name = input_data.validated_data.get('name', None)
            res = Restaurant.objects.create_restaurant(name, request.user.username)
            return Response({'status': 'success'}, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        restaurant = Restaurant.objects.get_current_user_restaurant(request.user.username)
        res = RestaurantSerializer(restaurant)
        return Response({'restaurant': res.data}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def get_all_menu(self, request):
        user = Account.objects.filter(username=self.request.user.username).first()
        restaurant = Restaurant.objects.filter(owner=user).first()
        menu = Menu.objects.get_all_menu_by_restaurant(restaurant)
        menus = MenuSerializer(menu, many=True)
        return Response({'menus': menus.data}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def create_menu(self, request):
        name = self.request.data['name']
        menu = Menu.objects.create_menu(name, request.user.username)
        menu = MenuSerializer(menu)
        return Response({'menu': menu.data}, status=status.HTTP_201_CREATED)


class MenuViewSet(ReadOnlyModelViewSet):
    serializer_class = MenuSerializer
    queryset = Menu.objects.get_all_available_menu()
    authentication_classes = [SessionAuthentication, BasicAuthentication, JWTAuthentication]
    permission_classes = [MenuPermission]


class VoteViewSet(ModelViewSet):
    queryset = MenuVote.objects.all()
    serializer_class = VoteSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication, JWTAuthentication]
    permission_classes = [IsEmployee]

    def create(self, request, *args, **kwargs):
        input_data = VoteSerializer(data=request.data)
        if input_data.is_valid():
            vote = MenuVote.objects.save_vote(self.request.user.username,
                                              input_data.validated_data.get('menu_id'))
            if vote:
                return Response({'status': 'success'}, status=status.HTTP_201_CREATED)
            return Response({'error': 'already voted'}, status=status.HTTP_406_NOT_ACCEPTABLE)

    def list(self, request, *args, **kwargs):
        res = MenuVote.objects.get_vote_status()
        return Response({'vote_status': res}, status=status.HTTP_200_OK)


class VoteResultViewSet(viewsets.ViewSet):

    def list(self, request):
        queryset = VoteResultTracker.objects.get_vote_result()

        return Response(queryset)

