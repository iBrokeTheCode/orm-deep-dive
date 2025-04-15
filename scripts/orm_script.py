from pprint import pprint

from django.db import connection
from django.db.models import F, Count, Q, Sum, Case, When, Avg, Value, Min, Max, CharField, Subquery, OuterRef, Exists
from django.db.models.functions import Coalesce
from django.contrib.auth.models import User

from django.contrib.contenttypes.models import ContentType

from itertools import count
from django.utils import timezone

from core.models import Staff, Restaurant, Rating, Sale, Comment, Event


def run():
    event = Event.objects.first()

    if event:
        print(event.start_date)
        print(event.end_date)
        print(event.duration)
        print(event.duration_in_days)
