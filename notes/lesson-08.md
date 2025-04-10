# Django ManyToManyFields and Through-Models for many-to-many relationships

## Covered Concepts

- [Many to Many Fields in Django](#many-to-many-fields-in-django)

## Reference

### Many to Many Fields in Django

Review the [documentation](https://docs.djangoproject.com/en/5.2/topics/db/examples/many_to_many/)

- **Many-to-many relationships** in Django (and [databases](https://en.wikipedia.org/wiki/Associative_entity)) allow **both sides of the relation to be connected to multiple objects on the other side**.
- Django uses **Junction tables (or association tables)** in the database to link two models together in a flexible many-to-many way.
- When you define a `models.ManyToManyField` in your Django model, Django implicitly creates this junction table.
- Example: A `Staff` model can have a `restaurants` field as a `models.ManyToManyField` linked to the `Restaurant` model, allowing one staff member to work at multiple restaurants and a restaurant to have multiple staff members.
- The junction table (e.g., `core_staff_restaurants`) contains **foreign keys to the IDs of both related models**.

```py
# models.py

class Staff(models.Model):
    name = models.CharField(max_length=128)
    restaurants = models.ManyToManyField(Restaurant)
```

### Next (6:30)

https://docs.djangoproject.com/en/5.2/topics/db/models/#extra-fields-on-many-to-many-relationships
