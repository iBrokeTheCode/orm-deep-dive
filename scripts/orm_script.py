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
    user = User.objects.first()
    restaurant = Restaurant.objects.first()

    rating = Rating.objects.create(
        user=user, restaurant=restaurant, rating=100
    )
    # rating = Rating.objects.update()

    print(rating)
