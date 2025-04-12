from pprint import pprint
import random

from django.db import connection
from django.db.models import F, Count, Q, Sum, Case, When, Avg, Value, Min, Max, CharField
from django.db.models.functions import Coalesce

from itertools import count
from django.utils import timezone

from core.models import Staff, Restaurant, Rating, Sale


def run():
    sales = Sale.objects.filter(restaurant__restaurant_type__in=['IN', 'IT'])
    print(len(sales))
    print(sales.values_list('restaurant__restaurant_type', flat=True).distinct())
