from django.utils import timezone

from core.models import Restaurant


def run():
    restaurant = Restaurant()
    restaurant.name = 'My Restaurant'
    restaurant.date_opened = timezone.now()
    restaurant.latitude = -50.25
    restaurant.longitude = -28.75
    restaurant.restaurant_type = Restaurant.TypeChoices.ITALIAN

    restaurant.save()
