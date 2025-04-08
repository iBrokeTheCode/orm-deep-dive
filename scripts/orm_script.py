from django.db import connection
from django.contrib.auth.models import User
from pprint import pprint

from core.models import Rating, Restaurant


def run():
    restaurant = Restaurant.objects.first()
    user = User.objects.first()
    rating, created = Rating.objects.get_or_create(
        restaurant=restaurant,
        user=user,
        rating=3
    )

    pprint(f'{rating} - {created}')
    pprint(connection.queries)
