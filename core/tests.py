from django.test import TestCase
from django.utils import timezone
from .models import Restaurant


class RestaurantTests(TestCase):
    def test_restaurant_name_property(self):
        restaurant = Restaurant(name='Test Restaurant')
        self.assertEqual(restaurant.restaurant_name, 'Test Restaurant')

        restaurant.nickname = 'Cool nickname'
        self.assertEqual(restaurant.restaurant_name, 'Cool nickname')

    def test_was_opened_this_year_property(self):
        restaurant = Restaurant(
            name='Test', date_opened=timezone.datetime(2024, 12, 12))

        self.assertEqual(restaurant.was_open_this_year, False)

        restaurant.date_opened = timezone.datetime(2025, 4, 17)
        self.assertEqual(restaurant.was_open_this_year, True)
