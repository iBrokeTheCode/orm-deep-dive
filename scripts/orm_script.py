from pprint import pprint
import random

from django.db import connection
from django.db.models import F, Count, Q

from core.models import Staff, Restaurant, Rating, Sale


def run():
    # has_a_number = Q(name__icontains=r'[0-9]+')
    restaurants = Restaurant.objects.filter(
        name__regex=r'[0-9]+').count()
    print(restaurants)

    pprint(connection.queries)
