# QuerySet Filtering and Lookups / Ordering and Slicing QuerySets

## Covered Concepts

- [Create custom commands](#create-custom-commands)
- [Filter, get and exists methods](#filter-get-and-exists-methods)
- [Filter with lookups](#filter-with-lookups)

## Reference

### Create custom commands

- Create the directory `management/commands` in your app
- Django will register a `manage.py` command for each Python module in that directory whose name doesn't begin with an underscore.
- Your command files must define a class `Command` that extends `BaseCommand`
- For more information, review [documentation](https://docs.djangoproject.com/en/5.1/howto/custom-management-commands/)
- In this lesson, we use the [`populate_db.py`](../core/management/commands/populate_db.py) module to populate our database.
- Run the command

  ```shell
  py manage.py populate_db
  ```

### Filter, get and exists methods

> [!NOTE]
> The `filter` method will return and empty QuerySet if the condition didn't met
> The `get` method will rise an exception if many records met the condition

```py
def run():
    restaurants = Restaurant.objects.filter( # SQL: WHERE
        restaurant_type=Restaurant.TypeChoices.ITALIAN)
    print(restaurants)
    print(restaurants.exists()) # Return True or False

    restaurant = Restaurant.objects.get(id=7)
```

### Filter with lookups

**AND operation**

```py
def run():
    restaurants = Restaurant.objects.filter( # SQL: AND
        restaurant_type=Restaurant.TypeChoices.CHINESE,
        name__startswith='C'
    )
```

**IN lookup**

```py
def run():
    filter_by = [Restaurant.TypeChoices.ITALIAN,
                 Restaurant.TypeChoices.CHINESE]
    restaurants = Restaurant.objects.filter( # SQL: IN
        restaurant_type__in=filter_by
    )
```

**exclude method**

```py
def run():
    filter_by = [Restaurant.TypeChoices.ITALIAN,
                 Restaurant.TypeChoices.CHINESE]
    restaurants = Restaurant.objects.exclude( # SQL: NOT
        restaurant_type__in=filter_by
    )
```

**lt, lte, gt, gte**

```py
def run():
    sales = Sale.objects.filter(income__lt=50) # SQL: <
    sales = Sale.objects.filter(income__lte=50) # SQL: <=
    sales = Sale.objects.filter(income__gt=50) # SQL: >
    sales = Sale.objects.filter(income__gte=50) # SQL: >=
```

**range**

```py
def run():
    sales = Sale.objects.filter(income__range=(20, 50)) # SQL: BETWEEN
```

**order by**

```py
def run():
    restaurants = Restaurant.objects.order_by('name')  # SQL: ORDER BY ... ASC
    restaurants = Restaurant.objects.order_by('name').reverse()  # SQL: ORDER BY ... DESC
    restaurants = Restaurant.objects.order_by('-name')  # SQL: ORDER BY ... DESC
```

**lower**

```py
from django.db.models.functions import Lower

def run():
    restaurants = Restaurant.objects.order_by(
        Lower('name'))  # SQL: ORDER BY ... LOWER ... ASC
```
