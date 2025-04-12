from pprint import pprint

from django.db import connection
from django.db.models import F, Count, Q, Sum, Case, When, Avg, Value, Min, Max, CharField, Subquery, OuterRef, Exists
from django.db.models.functions import Coalesce

from itertools import count
from django.utils import timezone

from core.models import Staff, Restaurant, Rating, Sale


def run():
    days_ago = timezone.now() - timezone.timedelta(days=5)

    restaurants = Restaurant.objects.filter(
        Exists(Sale.objects.filter(
            restaurant=OuterRef('pk'), datetime__gte=days_ago))
    )

    print(restaurants.count())
