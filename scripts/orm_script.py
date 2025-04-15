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
    first_sale = Sale.objects.first()
    if first_sale:
        print(
            f"Sale Income: {first_sale.income}, Suggested Tip: {first_sale.suggested_tip}")

    low_income_sale = Sale.objects.filter(income__lt=10).first()
    if low_income_sale:
        print(
            f"Sale Income: {low_income_sale.income}, Suggested Tip: {low_income_sale.suggested_tip}")
