from django.db import connection

from pprint import pprint

from core.models import Staff, Restaurant, StaffRestaurants


def run():
    staff = Staff.objects.first()
    restaurant = Restaurant.objects.get(id=7)

    staff.restaurants.add(restaurant, through_defaults={'salary': 67_000})
    print(staff.restaurants.all())

    # set 10 items
    # prefetch
