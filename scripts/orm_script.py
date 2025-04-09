from django.db import connection
from pprint import pprint

from django.db.models.functions import Lower

from core.models import Restaurant, Rating, Sale


def run():
    restaurants = Restaurant.objects.order_by(
        Lower('name'))  # SQL: ORDER BY ... LOWER ... ASC

    print(restaurants)

    pprint(connection.queries)

# Lower
