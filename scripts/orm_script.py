from django.db import connection
from pprint import pprint

from core.models import Restaurant


def run():
    restaurant = Restaurant.objects.get(id=1)
    pprint(restaurant.delete())

    pprint(connection.queries)
