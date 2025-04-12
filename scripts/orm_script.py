from pprint import pprint
import random

from django.db import connection
from django.db.models import F, Count, Q, Sum, Case, When, Avg, Value, Min, Max, CharField, Subquery
from django.db.models.functions import Coalesce

from itertools import count
from django.utils import timezone

from core.models import Staff, Restaurant, Rating, Sale


def run():
    restaurants = Restaurant.objects.filter(restaurant_type__in=('IT', 'CH'))
    print(restaurants)
