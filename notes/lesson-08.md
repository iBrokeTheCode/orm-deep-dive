# Django ManyToManyFields and Through-Models for many-to-many relationships

## Covered Concepts

- [Many to Many Fields in Django](#many-to-many-fields-in-django)
- [Querying Many to Many Fields in Django](#querying-many-to-many-fields-in-django)

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

### Querying Many to Many Fields in Django

Review [documentation](https://docs.djangoproject.com/en/5.2/topics/db/models/#extra-fields-on-many-to-many-relationships)

- First, can create Staff records with `get_or_create`, `save` or `create` methods. In this case, `name` is the only required field, because the `restaurants` is a many to many field.

  ```py
  def run():
      staff, created = Staff.objects.get_or_create(name='John Doe')
  ```

- When a model has a `models.ManyToManyField`, accessing that field (e.g., `staff.restaurants`) returns a **ManyRelatedManager**.
- This manager is specific to many-to-many relations and provides methods to manage the associated objects.

  ```py
  print(type(staff.restaurants)) # ...ManyRelatedManager
  ```

- You can fetch all related objects using the `.all()` method on the ManyRelatedManager. For example, `staff.restaurants.all()` would return all the restaurants associated with a staff member. Initially, this might return an empty queryset if no associations exist.

  ```py
  def run():
    staff, created = Staff.objects.get_or_create(name='John Doe')
    staff.restaurants.add(Restaurant.objects.first())

    print(staff.restaurants.all())
  ```

- You can get the number of associated objects using the `.count()` method (e.g., `staff.restaurants.count()`).

  ```py
  print(staff.restaurants.count())
  ```

- You can remove records with the `remove` method. If you pass an record that doesn't exist, wont' raise an exception.

  ```py
  staff.restaurants.remove(Restaurant.objects.first())
  ```

- Another methods you can use are `set` and `clear` methods. They allow us to create many associations and clear all associations respectively.

  ```py
  staff.restaurants.set(Restaurant.objects.all()[:3])
  staff.restaurants.clear()
  ```

- To filter the related objects, you can use the `.filter()` method on the ManyRelatedManager. This allows you to apply Django's query syntax to the related model. For instance, `staff.restaurants.filter(restaurant_type=Restaurant.type_choices.ITALIAN)` would return only the Italian restaurants associated with a staff member.

  ```py
  italian = staff.restaurants.filter(restaurant_type=Restaurant.TypeChoices.ITALIAN)
  print(italian)
  ```

- Standard Django query methods like `.exclude()` and `.order_by()` are also available on the ManyRelatedManager.
- You can access the related objects from the other side of the relationship as well. If the `Staff` model has a `restaurants` ManyToManyField, you can access all the staff members associated with a specific `Restaurant` instance using the **lowercase name of the model with the ManyToManyField, followed by `_set`**. For example, `restaurant.staff_set.all()` would return all the staff members associated with a particular restaurant.

  ```py
    class Staff(models.Model):
        name = models.CharField(max_length=128)
        restaurants = models.ManyToManyField(Restaurant, related_name='staff')

    # ---

    restaurant.staff_set.add(staff) # without related_name attribute
    restaurant.staff.remove(staff) # with related_name attribute
  ```

- The `_set` attribute also provides access to the ManyRelatedManager on the reverse side, allowing you to use methods like `.all()`, `.filter()`, `.count()`, etc..
