from pprint import pprint
import random

from django.db import connection
from django.db.models import F


from core.models import Staff, Restaurant, Rating, Sale


def run():
    sales = Sale.objects.all()
    for sale in sales:
        from decimal import Decimal
        sale.expenditure = Decimal(random.uniform(5, 100))
    Sale.objects.bulk_update(sales, ['expenditure'])

    pprint(connection.queries)
