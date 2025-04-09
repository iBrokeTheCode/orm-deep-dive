from django.db import connection
from pprint import pprint

from core.models import Restaurant, Rating, Sale


def run():
    restaurant_count = Restaurant.objects.count()
    rating_count = Rating.objects.count()
    sale_count = Sale.objects.count()

    pprint(f'{restaurant_count=}, {rating_count=}, {sale_count=}')

    pprint(connection.queries)
