from django.db import connection
from django.contrib.auth.models import User
from pprint import pprint

from core.models import Rating, Restaurant


def run():
    restaurant = Restaurant.objects.first()
    user = User.objects.first()
    rating = Rating(
        restaurant=restaurant,
        user=user,
        rating=20
    )
    rating.full_clean()
    rating.save()

    pprint(connection.queries)
