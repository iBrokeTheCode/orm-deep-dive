from pprint import pprint
import random

from django.db import connection
from django.db.models import F, Count, Q

from core.models import Staff, Restaurant, Rating, Sale


def run():
    rating = Rating.objects.get(id=7)
    if rating:
        print(rating.rating)
        rating.rating = F('rating') - 2
        rating.save()
        rating.refresh_from_db()

        print(rating.rating)

    # pprint(connection.queries)
