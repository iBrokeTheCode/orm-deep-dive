from django.shortcuts import render
from django.db.models import Sum, Prefetch
from django.utils import timezone

from .models import Restaurant, Sale


def index(request):
    # Get all 5-star ratings, and fetch all the sales for restaurants with 5-star ratings in the last month
    month_ago = timezone.now() - timezone.timedelta(days=30)
    monthly_sales = Prefetch(
        'sales',
        queryset=Sale.objects.filter(datetime__gte=month_ago)
    )

    restaurants = Restaurant.objects.prefetch_related(
        'ratings', monthly_sales).filter(ratings__rating=5)
    restaurants = restaurants.annotate(total=Sum('sales__income'))
    print([r.total for r in restaurants])

    print(restaurants)

    return render(request, 'core/index.html')
