# Models, Migrations and Admin UI Integration

## Covered Concepts

- [Models and Relationships](#models-and-relationships)
- Migrations: `python manage.py makemigrations` and `python manage.py migrate`
- `TextChoices`
- `on_delete`: `models.CASCADE` and `models.SET_NULL`
- [Register models in Admin panel](#registration)

## Reference

### Models and relationships

```python
# models.py
from django.db import models
from django.contrib.auth.models import User


class Restaurant(models.Model):
    class TypeChoices(models.TextChoices):
        INDIAN = ('IN', 'Indian')  # Tuple(to_db, to_form)
        CHINESE = ('CN', 'Chinese')
        ITALIAN = ('IT', 'Italian')
        GREEK = ('GR', 'Greek')
        MEXICAN = ('MX', 'Mexican')
        FAST_FOOD = ('FF', 'Fast Food')
        OTHER = ('OT', 'Other')

    name = models.CharField(max_length=100)
    website = models.URLField(default='')
    date_opened = models.DateField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    restaurant_type = models.CharField(
        max_length=2, choices=TypeChoices.choices)

    def __str__(self):
        return self.name


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()

    def __str__(self):
        return f'Rating: {self.rating}'


class Sale(models.Model):
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.SET_NULL, null=True)
    income = models.DecimalField(max_digits=8, decimal_places=2)
    datetime = models.DateTimeField()
```

### Registration

```python
# admin.py

from django.contrib import admin

from .models import Restaurant, Rating, Sale

admin.site.register(Restaurant)
admin.site.register(Rating)
admin.site.register(Sale)
```
