from django.shortcuts import render
from django.db.models import Sum, Prefetch
from django.utils import timezone

from .models import Restaurant, Sale, StaffRestaurants


def index(request):
    staff_restaurants = StaffRestaurants.objects.prefetch_related(
        'staff', 'restaurant')

    for record in staff_restaurants:
        print(record.restaurant.name)
        print(record.staff.name)

    return render(request, 'core/index.html')
