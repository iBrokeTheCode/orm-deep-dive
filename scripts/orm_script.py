from pprint import pprint

from django.db import connection
from django.db.models import F, Count, Q, Sum, Case, When, Avg, Value, Min, Max, CharField, Subquery, OuterRef, Exists
from django.db.models.functions import Coalesce
from django.contrib.auth.models import User

from django.contrib.contenttypes.models import ContentType

from itertools import count
from django.utils import timezone

from core.models import Staff, Restaurant, Rating, Sale, Comment


def run():
    restaurant = Restaurant.objects.last()

    if restaurant:
        restaurant.date_opened = timezone.datetime(year=2024, month=12, day=12)
        print(restaurant.date_opened)
        print(restaurant.was_open_this_year)
