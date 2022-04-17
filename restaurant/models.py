from django.db import models
from django.db.models import Max, Count
from django.utils.datetime_safe import date
from datetime import timedelta

from base.models import Account as User


class RestaurantManager(models.Manager):
    def create_restaurant(self, name, current_user):
        user = User.objects.filter(username=current_user).first()
        return self.create(name=name, owner=user)

    def get_restaurant_list(self):
        return self.select_related('owner').order_by('-id')

    def get_current_user_restaurant(self, current_user):
        user = User.objects.filter(username=current_user).first()
        return self.filter(owner=user).select_related('owner').first()  # only single restaurant per owner


class Restaurant(models.Model):
    owner = models.ForeignKey(User, on_delete=models.PROTECT)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = RestaurantManager()


class MenuManager(models.Manager):
    def create_menu(self, name, current_user):
        user = User.objects.filter(username=current_user).first()
        restaurant = Restaurant.objects.filter(owner=user).first()   # current design only supports
        return self.create(owner=restaurant, name=name)    # single restaurant for a particular owner!

    def get_all_available_menu(self):
        return self.filter(is_available=True).select_related('owner').order_by('id')

    def get_all_menu_by_restaurant(self, restaurant_owner):
        return self.filter(owner=restaurant_owner)


class Menu(models.Model):
    owner = models.ForeignKey(Restaurant, on_delete=models.PROTECT)
    name = models.CharField(max_length=100)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = MenuManager()


class MenuVoteManager(models.Manager):

    def save_vote(self, employee, menu_id):
        """
        Single employee can vote a menu for current date
        return false if already voted
        """
        user = User.objects.filter(username=employee).first()
        menu = Menu.objects.filter(pk=menu_id).first()
        if not self.filter(menu=menu, employee=user, created_at__startswith=date.today()).exists():
            self.create(menu=menu, employee=user)
            return True
        return False

    def get_vote_status(self):
        q = self.filter(created_at__startswith=date.today())
        return q.select_related('menu').values('menu__name', 'menu__owner__name').annotate(vote_count=Count('pk'))


class MenuVote(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.PROTECT)
    employee = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = MenuVoteManager()


class VoteResultTrackerManager(models.Manager):

    def get_vote_result(self):
        v_status = MenuVote.objects.get_vote_status()
        top_restaurant = v_status.latest('vote_count')  # get top voted menu and restaurant
        yesterday_res = VoteResultTracker.objects.filter(created_at__gte=date.today() - timedelta(1),
                                                         restaurant_name=top_restaurant['menu__owner__name']).exists()
        two_day_ago_res = VoteResultTracker.objects.filter(created_at__gte=date.today() - timedelta(2),
                                                           restaurant_name=top_restaurant['menu__owner__name']).exists()

        if yesterday_res and two_day_ago_res:
            second_highest_vote = list(v_status)[1]
            self.create(restaurant_name=second_highest_vote['menu__owner__name'])
            return {'restaurant_name': second_highest_vote['menu__owner__name'],
                    'menu_name': second_highest_vote['menu__name']}
        return {'restaurant_name': top_restaurant['menu__owner__name'], 'menu_name': top_restaurant['menu__name']}


class VoteResultTracker(models.Model):
    restaurant_name = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = VoteResultTrackerManager()
