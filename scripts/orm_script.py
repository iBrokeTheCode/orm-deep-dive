from django.db import connection
from django.db.models.functions import Upper

from core.models import Staff, Restaurant, StaffRestaurants


def run():
    restaurants = Restaurant.objects.values(upper_name=Upper('name'))
    print(restaurants)
