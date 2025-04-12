from pprint import pprint
import random

from django.db import connection
from django.db.models import F, Count, Q, Sum, Case, When
from django.db.models.functions import Coalesce

from core.models import Staff, Restaurant, Rating, Sale


def run():
    restaurants = Restaurant.objects.annotate(
        num_sales=Count('sales')).annotate(
            is_popular=Case(
                When(
                    num_sales__gt=8, then=True
                ), default=False
            )
    ).values('num_sales', 'is_popular')
    print(restaurants)

    # TODO: Continues as 9:12

    # pprint(connection.queries)
