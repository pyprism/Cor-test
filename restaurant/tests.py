from datetime import timedelta

from django.test import TestCase
from rest_framework.reverse import reverse
from django.utils.datetime_safe import date

from .models import Restaurant, Menu, MenuVote, VoteResultTracker
from base.models import Account
from rest_framework.test import APIClient


class RestaurantApiTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin = Account.objects.create_superuser("admin", "admin")
        self.user = Account.objects.create_user("user", "user", is_restaurant_owner=True)

    def test_only_restaurant_owner_can_access_endpoint(self):
        self.client.force_authenticate(user=self.admin)
        res = self.client.get(reverse('restaurant-list'), format="json")
        self.assertEqual(res.status_code, 403)

        self.client.logout()

        self.client.force_authenticate(user=self.user)
        res = self.client.get(reverse('restaurant-list'), format="json")
        self.assertEqual(res.status_code, 200)

    def test_create_restaurant(self):
        self.client.force_authenticate(user=self.user)
        data = {"name": "restaurant"}
        res = self.client.post(reverse('restaurant-list'), format="json", data=data)
        self.assertEqual(res.status_code, 201)

    def test_menu_creation_for_own_restaurant(self):
        self.client.force_authenticate(user=self.user)
        Restaurant.objects.create_restaurant("example", self.user)
        data = {"name": "NULL porota"}
        res = self.client.post(reverse('restaurant-create-menu'), format="json", data=data)
        self.assertEqual(res.status_code, 201)

    def test_owner_can_see_all_menu(self):
        self.test_menu_creation_for_own_restaurant()
        res = self.client.get(reverse('restaurant-get-all-menu'))
        self.assertEqual(res.status_code, 200)
        response = res.json()
        self.assertEqual(response, {'menus': [{'id': 1, 'name': 'NULL porota', 'owner': {'id': 1, 'name': 'example'}}]})


class MenuEndpointTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin = Account.objects.create_superuser("admin", "admin")
        self.user = Account.objects.create_user("user", "user", is_employee=True)
        self.owner = Account.objects.create_user("res", "res", is_restaurant_owner=True)
        Restaurant.objects.create_restaurant("example", self.owner)
        Menu.objects.create_menu("kola", self.owner.username)

    def test_employee_can_access_endpoint(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.get(reverse('menu-list'))
        self.assertEqual(res.status_code, 200)

    def test_admin_cannot_access_endpoint(self):
        self.client.force_authenticate(user=self.admin)
        res = self.client.get(reverse('menu-list'))
        self.assertEqual(res.status_code, 403)

    def test_correct_response(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.get(reverse('menu-list'))
        self.assertEqual(res.json(), {'count': 1, 'next': None, 'previous': None,
                                      'results': [{'id': 1, 'name': 'kola', 'owner': {'id': 1, 'name': 'example'}}]})


class VoteEndpointTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin = Account.objects.create_superuser("admin", "admin")
        self.user = Account.objects.create_user("user", "user", is_employee=True)
        self.owner = Account.objects.create_user("res", "res", is_restaurant_owner=True)
        Restaurant.objects.create_restaurant("example", self.owner)
        Menu.objects.create_menu("alu", self.owner.username)
        Menu.objects.create_menu("kola", self.owner.username)

    def test_only_employee_can_access_endpoint(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.get(reverse('menuvote-list'))
        self.assertEqual(res.status_code, 200)

        self.client.logout()

        self.client.force_authenticate(user=self.admin)
        res = self.client.get(reverse('menu-list'))
        self.assertEqual(res.status_code, 403)

    def test_employee_voting(self, menu_id=1):
        self.client.force_authenticate(user=self.user)
        res = self.client.post(reverse('menuvote-list'), format='json', data={'menu_id': menu_id})
        self.assertEqual(res.status_code, 201)

    def test_vote_status(self):
        self.test_employee_voting(1)
        self.test_employee_voting(2)
        res = self.client.get(reverse('menuvote-list'))
        self.assertEqual(res.json(), {'vote_status': [{'menu__name': 'alu', 'menu__owner__name': 'example',
                                                       'vote_count': 1}, {'menu__name': 'kola',
                                                                          'menu__owner__name': 'example',
                                                                          'vote_count': 1}]})


class VoteResultEndpointTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.owner = Account.objects.create_user("res", "res", is_restaurant_owner=True)
        self.owner2 = Account.objects.create_user("res1", "res1", is_restaurant_owner=True)
        self.employee = Account.objects.create_user("user", "user", is_employee=True)
        self.employee2 = Account.objects.create_user("user2", "user2", is_employee=True)
        self.employee3 = Account.objects.create_user("user3", "user3", is_employee=True)

        Restaurant.objects.create_restaurant("Restaurant 1", self.owner)
        Restaurant.objects.create_restaurant("Restaurant 2", self.owner2)

        self.r1 = Menu.objects.create_menu("alu", self.owner.username)
        self.r2 = Menu.objects.create_menu("chicken", self.owner2.username)

        MenuVote.objects.save_vote(self.employee, self.r1.id)
        MenuVote.objects.save_vote(self.employee2, self.r1.id)
        MenuVote.objects.save_vote(self.employee3, self.r2.id)

    def test_vote_result(self):
        res = self.client.get(reverse('vote_result-list'))
        self.assertEqual(res.json(), {'restaurant_name': 'Restaurant 1', 'menu_name': 'alu'})

    def test_not_winner_for_3_consecutive_days(self):
        yesterday = date.today() - timedelta(1)
        two_days = date.today() - timedelta(2)
        VoteResultTracker.objects.create(restaurant_name='Restaurant 1', created_at=yesterday)
        VoteResultTracker.objects.create(restaurant_name='Restaurant 1', created_at=two_days)

        res = self.client.get(reverse('vote_result-list'))

        self.assertEqual(res.json(), {'restaurant_name': 'Restaurant 2', 'menu_name': 'chicken'})
