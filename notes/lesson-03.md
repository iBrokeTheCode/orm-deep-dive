# Querying and Creating Records / Working with Foreign Keys

## Covered Concepts

- [RunScript](#runscript)
- [Create records](#create-records)
- [View Executed Query](#view-executed-query)
- [Common Commands](#common-commands)
- [Relationship Backward](#relationship-backward)
- [Get or Create](#get-or-create)

## Reference

### RunScript

- Review [documentation](https://django-extensions.readthedocs.io/en/latest/runscript.html)
- Create a directory `scripts`

```shell
mkdir scripts
touch scripts/__init__.py
touch scripts/my_script.py
```

- Run the script with the command

```shell
py manage.py runscript my_script
```

### Create Records

```python
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

    Restaurant.objects.create(
        name='My succursal',
        date_opened=timezone.now(),
        latitude=-25.59,
        longitude=-135.25,
        restaurant_type=Restaurant.TypeChoices.GREEK
    )
```

### View Executed Query

```python
from django.db import connection

from core.models import Restaurant

def run():
    restaurants = Restaurant.objects.all()
    # print(restaurants) # Lazy load []

    print(connection.queries) # LIMIT 21
```

Also can use the `python manage.py shell_plus --print-sql` to run a interactive shell that display executed queries. Here you can use statements like `restaurants = Restaurant.objects.all()`

### Common Commands

```python
from django.utils import timezone
from core.models import Restaurant

def run():
    restaurants = Restaurant.objects.all()
    restaurant_first = Restaurant.objects.first()
    restaurant_last = Restaurant.objects.last()
    count = Restaurant.objects.count()
```

### Filters and lookups

Review the [list of lookups](https://medium.com/dajngo/lookup-expressions-in-django-61715708dd6f)

```python
from pprint import pprint
from django.db import connection

from core.models import Rating

def run():
    ratings = Rating.objects.filter(rating=3) # SQL -> ... WHERE
    ratings = Rating.objects.filter(rating__gte=3)
    ratings = Rating.objects.filter(rating__lte=3)
    ratings = Rating.objects.exclude(rating__gt=3) # SQL -> ... WHERE NOT
    pprint(ratings)
    pprint(connection.queries)
```

> [!NOTE]
> If you call for example `rating.restaurant`, Django will execute 2 SQL queries: one to get the rating instance and other to get data of the restaurant

### Relationship Backward

Review [documentation](https://docs.djangoproject.com/en/5.2/topics/db/queries/#following-relationships-backward)

```python
# models.py
class Sale(models.Model):
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.SET_NULL, null=True, related_name='sales')
    income = models.DecimalField(max_digits=8, decimal_places=2)
    datetime = models.DateTimeField()
```

```python
# orm_script.py

from django.db import connection
from pprint import pprint

from core.models import Restaurant

def run():
    restaurant = Restaurant.objects.first()
    # print(restaurant.rating_set.all())
    print(restaurant.ratings.all())

    pprint(connection.queries)
```

### Get or Create

```python
from django.db import connection
from django.contrib.auth.models import User
from pprint import pprint

from core.models import Rating, Restaurant


def run():
    restaurant = Restaurant.objects.first()
    user = User.objects.first()
    rating, created = Rating.objects.get_or_create(
        restaurant=restaurant,
        user=user,
        rating=3
    )

    pprint(f'{rating} - {created}')
    pprint(connection.queries)
```
