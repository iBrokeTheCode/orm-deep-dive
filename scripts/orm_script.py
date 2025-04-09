from django.db import connection
from pprint import pprint

from core.models import Restaurant


def run():
    restaurants = Restaurant.objects.all()
    restaurants.update(website='http://example.com')

    pprint(connection.queries)
