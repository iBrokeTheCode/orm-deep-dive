from pprint import pprint

from django.db import connection
from django.db.models import F, Count, Q, Sum, Case, When, Avg, Value, Min, Max, CharField, Subquery, OuterRef, Exists
from django.db.models.functions import Coalesce

from django.contrib.contenttypes.models import ContentType

from itertools import count
from django.utils import timezone

from core.models import Staff, Restaurant, Rating, Sale, Comment


def run():
    restaurant = Restaurant.objects.get(pk=4)
    restaurant.comments.add(
        Comment.objects.create(text='I change my mind',
                               content_object=restaurant)
    )
