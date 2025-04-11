from django.db import connection
from django.db.models import Count, Avg, Sum, Min, Max

from django.utils import timezone

from core.models import Staff, Restaurant, Rating, Sale


def run():
    last_month = timezone.now() - timezone.timedelta(days=31)

    sales = Sale.objects.filter(datetime__gte=last_month).aggregate(
        minimum=Min('income'),
        maximum=Max('income'),
        avg=Avg('income'),
        sum=Sum('income'),
        count=Count('id'),
    )
    print(sales)

    print(connection.queries)
