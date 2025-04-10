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

### Customizing Many-to-Many Fields with Through Models in Django

Review [documentation](https://docs.djangoproject.com/en/5.2/topics/db/models/#extra-fields-on-many-to-many-relationships)

- **The Need for Extra Data:** Sometimes, you need to store additional information _about_ the relationship itself, not just which objects are related. For instance, you might want to record a staff member's salary at a specific restaurant or their start date at that location.

- **The `through` Argument:** Django allows you to specify a model to be used to manage the many-to-many relationship instead of relying on the implicitly created junction table. This is done using the **`through` keyword argument** in the `models.ManyToManyField` definition.

- **Defining a Through Model:** When you use the `through` argument, you need to create a separate Django model that will act as the intermediary or "through" model. This model **must contain foreign keys to both of the models involved in the many-to-many relationship**.

- **Custom Fields in the Through Model:** The primary benefit of using a through model is the ability to **add custom fields** to it. These fields can store the extra information relevant to the relationship, such as salary, start date, role, etc..

#### Implementation

To customize a many-to-many field with a through model:

1.  **Define the Many-to-Many Field with the `through` Argument:** In one of your models, define the `ManyToManyField` and specify the name of your custom through model using the `through` keyword argument. For example, in the `Staff` model:

    ```python
    from django.db import models

    class Restaurant(models.Model):
        name = models.CharField(max_length=100)
        # ... other fields ...

    class StaffRestaurant(models.Model):
        staff = models.ForeignKey('Staff', on_delete=models.CASCADE)
        restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
        salary = models.FloatField(null=True)
        # ... other custom fields ...

        class Meta:
            unique_together = ('staff', 'restaurant') # Recommended to prevent duplicate entries

    class Staff(models.Model):
        name = models.CharField(max_length=100)
        restaurants = models.ManyToManyField(Restaurant, through='StaffRestaurant')
        # ... other fields ...
    ```

2.  **Create the Through Model:** Define the Django model specified in the `through` argument. This model **must have `ForeignKey` fields pointing to both models** involved in the many-to-many relationship. In the example above, `StaffRestaurant` has foreign keys to `Staff` and `Restaurant`, as well as an additional `salary` field.

3.  **Make Migrations:** After defining your models, you need to create and apply migrations to update your database schema.

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

#### Working with Through Models

Once you have set up a many-to-many relationship with a through model, interacting with the related objects and the extra data requires using the through model directly or leveraging the many-related manager with specific methods:

- **Creating Associations Directly Through the Through Model:** You can create associations by creating instances of the through model and explicitly linking the related objects and setting the values for any extra fields:

  ```python
  john = Staff.objects.get(name='John Wick')
  italian_place = Restaurant.objects.get(name='Italian Place')

  # Create an association with a salary
  StaffRestaurant.objects.create(staff=john, restaurant=italian_place, salary=28000)
  ```

- **Querying Through Model Data:** You can query the through model directly to access the extra information for specific relationships:

  ```python
  john_restaurants = StaffRestaurant.objects.filter(staff=john)
  for association in john_restaurants:
      print(f"{john.name} works at {association.restaurant.name} with a salary of ${association.salary}")
  ```

- **Using the Many-Related Manager with `through_defaults`:** You can still use the many-related manager's `add()` and `set()` methods on the model that defines the `ManyToManyField`. To set values for the extra fields in the through model, use the **`through_defaults`** keyword argument with a dictionary mapping the through model's field names to the desired values:

  ```python
  john = Staff.objects.get(name='John Wick')
  another_restaurant = Restaurant.objects.get(pk=...)

  # Adding a single restaurant with a salary
  john.restaurants.add(another_restaurant, through_defaults={'salary': 24000})

  # Setting multiple restaurants with salaries
  restaurants = Restaurant.objects.all()[:5]
  john.restaurants.set(restaurants, through_defaults={'salary': 30000}) # All will have the same salary here
  ```

- **Accessing Related Objects from the Other Side:** You can still access the related objects from the other side of the many-to-many relationship using the convention `modelname_set` (lowercase model name followed by `_set`) if the relationship is not explicitly defined on that model. You can then use `.all()` and other query methods on this related manager.

#### Important Considerations

- **Initial Setup:** It is generally easier to define the `through` model when you initially create the many-to-many relationship. **Adding or removing the `through` argument to an existing `ManyToManyField` can be problematic and may require significant database modifications or even re-creation**.

- **Query Optimization with `prefetch_related`:** When working with through models, you might need to access data from the through model and the related parent models. To optimize database queries and avoid excessive lookups within loops, use Django's **`prefetch_related()`** method. You can prefetch both the related model and the through model:

  ```python
  jobs = StaffRestaurant.objects.prefetch_related('staff', 'restaurant').all()
  for job in jobs:
      print(f"{job.staff.name} at {job.restaurant.name} (${job.salary})")
  ```

By using through models, you gain more control and flexibility over your many-to-many relationships in Django, allowing you to store and manage additional information associated with the links between your models.
