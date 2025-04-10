from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.db.models.functions import Lower


def start_with_a_validator(name: str):
    if not name.lower().startswith('a'):
        raise ValidationError('Restaurant name must start with a')


class Restaurant(models.Model):
    class TypeChoices(models.TextChoices):
        INDIAN = ('IN', 'Indian')  # Tuple(to_db, to_form)
        CHINESE = ('CN', 'Chinese')
        ITALIAN = ('IT', 'Italian')
        GREEK = ('GR', 'Greek')
        MEXICAN = ('MX', 'Mexican')
        FAST_FOOD = ('FF', 'Fast Food')
        OTHER = ('OT', 'Other')

    class Meta:
        ordering = (Lower('name'), )
        get_latest_by = ('date_opened')

    name = models.CharField(max_length=100, validators=[
                            start_with_a_validator])
    website = models.URLField(default='')
    date_opened = models.DateField()
    latitude = models.FloatField(
        validators=[MinValueValidator(-90), MaxValueValidator(90)]
    )
    longitude = models.FloatField(
        validators=[MinValueValidator(-180), MaxValueValidator(180)]
    )
    restaurant_type = models.CharField(
        max_length=2, choices=TypeChoices.choices)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        print(self._state.adding)
        super().save(*args, **kwargs)


class Staff(models.Model):
    name = models.CharField(max_length=128)
    restaurants = models.ManyToManyField(
        Restaurant, related_name='staff', through='StaffRestaurants')

    def __str__(self):
        return self.name


class StaffRestaurants(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    salary = models.FloatField(null=True)


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name='ratings')
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    def __str__(self):
        return f'Rating: {self.rating}'


class Sale(models.Model):
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.SET_NULL, null=True, related_name='sales')
    income = models.DecimalField(max_digits=8, decimal_places=2)
    datetime = models.DateTimeField()
