from pprint import pprint
import random

from django.db import connection
from django.db.models import F, Count, Q, Sum
from django.db.models.functions import Coalesce

from core.models import Staff, Restaurant, Rating, Sale


def run():
    restaurant = Restaurant.objects.first()

    if restaurant:
        restaurant.nickname = 'Cool nickname'
        restaurant.save()
    nicknames = Restaurant.objects.annotate(
        new_field=Coalesce(F('nickname'), F('name'))).values('new_field')
    print(nicknames)

    # pprint(connection.queries)
