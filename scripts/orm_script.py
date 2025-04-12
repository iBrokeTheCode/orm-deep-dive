from pprint import pprint
import random

from django.db import connection
from django.db.models import F, Count, Q, Sum, Case, When, Avg, Value, Min, Max, CharField
from django.db.models.functions import Coalesce

from itertools import count
from django.utils import timezone

from core.models import Staff, Restaurant, Rating, Sale


def run():
    first_sale = Sale.objects.aggregate(first_sale_date=Min('datetime'))[
        'first_sale_date']
    last_sale = Sale.objects.aggregate(last_dale_date=Max('datetime'))[
        'last_dale_date']

    dates = []
    counter = count(0)
    dt = first_sale

    while (dt := first_sale + timezone.timedelta(days=10*next(counter))) <= last_sale:
        dates.append(dt)

    whens = [
        When(
            datetime__range=(dt, dt + timezone.timedelta(days=10)),
            then=Value(dt.date())
        )
        for dt in dates
    ]

    case = Case(*whens, output_field=CharField())

    sales_by_date_range = Sale.objects.annotate(
        date_range=case
    ).values('date_range').annotate(total_sales=Sum('income')).order_by('date_range')

    for item in sales_by_date_range:
        print(
            f"Date Range: {item['date_range']}, Total Sales: {item['total_sales']}")
