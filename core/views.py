from django.shortcuts import render
from django.db.models import Sum

from .models import Restaurant, Rating


def index(request):
    # Get all 5-star ratings, and fetch all the sales for restaurants with 5-star ratings.
    restaurants = Restaurant.objects.prefetch_related(
        'ratings', 'sales').filter(ratings__rating=5).annotate(total=Sum('sales__income'))

    print(restaurants)

    return render(request, 'core/index.html')
