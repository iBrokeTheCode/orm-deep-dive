from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.db.models.functions import Lower
from django.db.models import Q

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation

from django.urls import reverse
from django.utils import timezone
from datetime import datetime


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

        constraints = [
            models.CheckConstraint(
                check=Q(latitude__gte=-90) & Q(latitude__lte=90),
                name='valid_latitude',
                violation_error_message='Latitude must be between -90 and 90'
            ),
            models.CheckConstraint(
                check=Q(longitude__gte=-180, longitude__lte=180),
                name='valid_longitude',
                violation_error_message='Latitude must be between -180 and 180'
            ),
            models.UniqueConstraint(
                Lower('name'), name='restaurant_name_unique_insensitive'
            )
        ]

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
    capacity = models.PositiveSmallIntegerField(null=True)
    nickname = models.CharField(max_length=100, default='')
    comments = GenericRelation('Comment', related_query_name='restaurant')

    @property
    def restaurant_name(self) -> str:
        return self.nickname or self.name

    @property
    def was_opened_this_year(self):
        current_year = timezone.now().year

        return self.date_opened.year == current_year

    def is_open_after(self, reference_date: datetime):
        return self.date_opened > reference_date

    def get_absolute_url(self):
        return reverse('core:restaurant_detail', kwargs={'pk': self.pk})

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
    comments = GenericRelation('Comment')

    class Meta:
        constraints = [
            models.CheckConstraint(
                name='rating_valid_value',
                # check=Q(rating__gte=1, rating__lte=5),
                check=Q(rating__range=(1, 5)),
                violation_error_message='Invalid rating, It must be between 1 and 5'
            )
        ]

    def __str__(self):
        return f'Rating: {self.rating}'


class Sale(models.Model):
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.SET_NULL, null=True, related_name='sales')
    income = models.DecimalField(max_digits=8, decimal_places=2)
    expenditure = models.DecimalField(max_digits=8, decimal_places=2)
    datetime = models.DateTimeField()


class Product(models.Model):
    name = models.CharField(max_length=255)
    number_in_stock = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.name


class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    number_of_items = models.PositiveSmallIntegerField()

    def __str__(self):
        return f'{self.number_of_items} x {self.product.name}'


class Comment(models.Model):
    text = models.TextField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
