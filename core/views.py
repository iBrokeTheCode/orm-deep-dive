from django.shortcuts import render

from .models import Restaurant


def index(request):
    restaurants = Restaurant.objects.all()

    context = {
        'restaurants': restaurants
    }

    return render(request, 'core/index.html', context)
