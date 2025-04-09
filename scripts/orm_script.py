from django.db import connection
from pprint import pprint

from django.db.models.functions import Lower

from core.models import Restaurant, Rating, Sale


def run():
    restaurants = Sale.objects.filter(restaurant__name__startswith='C')
    print(restaurants)

    pprint(connection.queries)

# django debug toolbar
