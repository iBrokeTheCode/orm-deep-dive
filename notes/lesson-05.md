# Updating and Deleting QuerySets / ForeignKey on_delete behaviour

## Covered Concepts

- [Update records](#update-records)
- [Field Lookups](#field-lookups)
- [Delete records](#delete-records)

## Reference

### Update Records

By default, the `save` method update all fields. Can indicate the `update_fields` to only update an specific field.

```py
from django.db import connection
from pprint import pprint

from core.models import Restaurant


def run():
    restaurant = Restaurant.objects.last()
    if restaurant is not None:
        restaurant.name = 'My Succursal'
        restaurant.save(update_fields=('name',))
    else:
        print("No restaurant found in the database.")

    pprint(connection.queries)
```

**Overwrite `save` method**

Can overwrite `save` method. In this case, `self._state.adding` prints True if the instance is created and False if the instance is updated when calling the `save` method. Review [documentation](https://docs.djangoproject.com/en/5.2/ref/models/instances/#state)

```py
# models.py
class Restaurant(models.Model):
    # ...

    def save(self, *args, **kwargs):
        print(self._state.adding)
        super().save(*args, **kwargs)
```

### Update multiple objects at once

Review [documentation](https://docs.djangoproject.com/en/5.2/topics/db/queries/#updating-multiple-objects-at-once)

In this example, all Restaurant instance will update their website field.

```py
# orm_script.py
def run():
    restaurants = Restaurant.objects.all()
    restaurants.update(website='http://example.com')

    pprint(connection.queries)
```

> [!NOTE]
> The `update` method is more efficient that iterate and call `save` method (each `save` execute an SQL query)
> The `update` method don't run the overwrite login in `save` method
> The `update` method returns the number of affected records in database

### Field Lookups

Review [documentation](https://docs.djangoproject.com/en/5.2/topics/db/queries/#field-lookups)

```py

def run():
    restaurants = Restaurant.objects.filter(name__icontains='restaurant')
    restaurants = Restaurant.objects.filter(name__startswith='restaurant')
    restaurants = Restaurant.objects.filter(name__iexact='restaurant')
    pprint(restaurants)


    pprint(connection.queries)
```

### Delete records

> [!WARNING]
> The `delete` method returns the total number of affected records and a dictionary with models and record affected.
> Be careful with the `on_delete` property. In `CASCADE` the foreign key relationships will be deleted (first child then parent)
> In `SET_NULL`, the foreign key relationship will be set to null value.

```py
# orm_script.py
def run():
    restaurant = Restaurant.objects.get(id=1)
    pprint(restaurant.delete())

    pprint(connection.queries)
```

```shell
(2, {'core.Rating': 1, 'core.Restaurant': 1})
```

```py
# orm_script.py
def run():
    # Deletes all Restaurant instances
    restaurants = Restaurant.objects.all().delete()
```
