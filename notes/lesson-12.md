# Django - Handling NULL Values in the Database

## Concepts

- **Adding Nullable Columns:** You can add nullable columns to your Django models by setting the `null=True` keyword argument in the field definition. For form handling, you might also want to set `blank=True`. Read [documentation](https://docs.djangoproject.com/en/5.2/ref/models/fields/#null)

  ```py
  capacity = models.PositiveSmallIntegerField(null=True, blank=True)
  ```

  Running `python manage.py makemigrations` and `python manage.py migrate` will apply these changes to your database schema. In the database, a nullable column will typically not have a "NOT NULL" constraint.

- **Querying for NULL Values:** Django's ORM provides the `isnull` lookup to filter records based on whether a field's value is NULL. Read [documentation](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#isnull)

  - **Finding records where a field is NULL:**

    ```pyt
    restaurants_with_null_capacity = Restaurant.objects.filter(capacity__isnull=True)
    ```

    This generates an SQL query that checks `capacity IS NULL`.

  - **Finding records where a field is NOT NULL:**
    ```py
    restaurants_with_non_null_capacity = Restaurant.objects.filter(capacity__isnull=False)
    ```
    This generates an SQL query that checks `capacity IS NOT NULL`.
  - You can also use `.exclude()` with `isnull=False` to achieve the same result as filtering for non-null values.
  - `.count()` can be chained to get the number of records with null or non-null values.
    ```py
    non_null_capacity_count = Restaurant.objects.filter(capacity__isnull=False).count()
    ```

- **Handling NULL Values in Ordering:** By default, when ordering by a nullable field, Django places NULL values at the beginning of the queryset.

  ```py
  restaurants_ordered_by_capacity = Restaurant.objects.order_by('capacity').values('capacity')
  ```

  To customize the ordering of NULL values, you can use the `F` expression with `.asc()` and `.desc()` and the `nulls_last` parameter.

  ```py
  from django.db.models import F

  # Order with NULL values at the end (ascending order for non-nulls)
  restaurants_ordered_nulls_last_asc = Restaurant.objects.order_by(F('capacity').asc(nulls_last=True)).values('capacity')

  # Order with NULL values at the end (descending order for non-nulls)
  restaurants_ordered_nulls_last_desc = Restaurant.objects.order_by(F('capacity').desc(nulls_last=True)).values('capacity')
  ```

  You can also filter out NULL values before ordering if you don't want them in the result.

  ```py
  restaurants_without_nulls_ordered = Restaurant.objects.filter(capacity__isnull=False).order_by('capacity').values('capacity')
  ```

- **The `coalesce` Function:** The `coalesce` database function (available in Django via `django.db.models.functions.Coalesce`) allows you to provide a fallback value when a field or expression evaluates to NULL. It takes a list of at least two field names or expressions and returns the first non-null value from the list. Read [documentation](https://docs.djangoproject.com/en/5.2/ref/models/database-functions/#coalesce)

  ```py
  from django.db.models.functions import Coalesce
  from django.db.models import Sum, Avg, F
  ```

  - **Providing a default value for a sum aggregation:**

    ```py
    # Initially setting all capacities to NULL
    Restaurant.objects.update(capacity=None)

    total_capacity_with_default = Restaurant.objects.aggregate(
        total_capacity=Coalesce(Sum('capacity'), 0)
    )
    ```

    Here, if `Sum('capacity')` returns NULL (because all capacity values are NULL), `coalesce` will return `0`.

  - **Providing a default value for an average aggregation over an empty queryset:**

    ```py
    average_rating_with_default = Rating.objects.filter(rating__lt=0).aggregate(
        average_rating=Coalesce(Avg('rating'), 0.0)
    )
    ```

    If the filter returns an empty queryset, `Avg('rating')` would be NULL, and `coalesce` will return `0.0`.

  - **Providing a fallback value when annotating a queryset:**
    ```py
    # Assuming a Restaurant model with 'name' and a nullable 'nickname' field
    restaurants_with_name_value = Restaurant.objects.annotate(
        name_value=Coalesce('nickname', 'name')
    ).values('name_value')
    ```
    This will first try to get the `nickname`. If the `nickname` is NULL, it will fall back to the `name`.

- **Caveat: `null=True` on String-Based Fields:** It's generally recommended to avoid using `null=True` on string-based fields like `CharField` and `TextField`. For representing missing string data, use `default=''` (empty string) instead. This avoids having two representations for "no data" (NULL and empty string). For example:

  ```py
  website = models.URLField(default='')
  ```

- **Default Value in Aggregation Functions:** Django's aggregation functions like `Avg` also accept a `default` keyword argument. This provides a value to return when the aggregation is performed over an empty queryset, often negating the need for `coalesce` in such cases.
  ```py
  average_rating_with_aggregation_default = Rating.objects.filter(rating__lt=0).aggregate(
      average_rating=Avg('rating', default=0.0)
  )
  ```
  Under the hood, Django might use the database's `COALESCE` function when you provide a `default` to an aggregate function.

## Examples

- **Adding a nullable `capacity` field to the `Restaurant` model:**

  ```py
  # In models.py
  class Restaurant(models.Model):
      # ... other fields ...
      capacity = models.PositiveSmallIntegerField(null=True, blank=True)
      # ... other fields ...
  ```

- **Querying for restaurants with NULL and NOT NULL `capacity`:**

  ```py
  # In ormscript.py
  from core.models import Restaurant

  restaurants_with_null_capacity = Restaurant.objects.filter(capacity__isnull=True)
  restaurants_with_non_null_capacity = Restaurant.objects.filter(capacity__isnull=False)
  ```

- **Setting `capacity` for specific restaurants:**

  ```py
  restaurant1 = Restaurant.objects.first()
  restaurant2 = Restaurant.objects.last()
  restaurant1.capacity = 10
  restaurant2.capacity = 20
  restaurant1.save()
  restaurant2.save()
  ```

- **Ordering by `capacity`:**

  ```py
  from django.db.models import F
  # (NULLs first by default)
  restaurants_ordered_by_capacity = Restaurant.objects.order_by('capacity').values('capacity')

  # with NULLs last (ascending):
  restaurants_ordered_nulls_last_asc = Restaurant.objects.order_by(F('capacity').asc(nulls_last=True)).values('capacity')

  # with NULLs last (descending)
  restaurants_ordered_nulls_last_desc = Restaurant.objects.order_by(F('capacity').desc(nulls_last=True)).values('capacity')

  # Filtering out NULLs before ordering
  restaurants_without_nulls_ordered_asc = Restaurant.objects.filter(capacity__isnull=False).order_by('capacity').values('capacity')
  restaurants_without_nulls_ordered_desc = Restaurant.objects.filter(capacity__isnull=False).order_by('-capacity').values('capacity')

  ```

- **Using `Coalesce` with `Sum` to provide a default of 0:**

  ```py
  from django.db.models import Sum
  from django.db.models.functions import Coalesce

  Restaurant.objects.update(capacity=None) # Resetting capacity to NULL for all restaurants

  total_capacity_with_default = Restaurant.objects.aggregate(
      total_capacity=Coalesce(Sum('capacity'), 0)
  )
  ```

- **Using `Coalesce` with `Avg` to provide a default of 0.0:**

  ```py
  from django.db.models import Avg

  average_rating_with_default_coalesce = Rating.objects.filter(rating__lt=0).aggregate(
      average_rating=Coalesce(Avg('rating'), 0.0)
  )
  ```

- **Using the `default` argument in `Avg`:**

  ```py
  average_rating_with_aggregation_default = Rating.objects.filter(rating__lt=0).aggregate(
      average_rating=Avg('rating', default=0.0)
  )
  ```

- **Adding a nullable `nickname` field to the `Restaurant` model:**

  ```py
  # In models.py
  class Restaurant(models.Model):
      # ... other fields ...
      nickname = models.CharField(max_length=200, blank=True)
      # ... other fields ...
  ```

- **Using `Coalesce` to get `nickname` if available, otherwise `name`:**

  ```py
  from django.db.models import F
  from django.db.models.functions import Coalesce

  restaurants_with_name_value = Restaurant.objects.annotate(
      name_value=Coalesce('nickname', 'name')
  ).values('name_value')

  # Setting a nickname for the first restaurant
  first_restaurant = Restaurant.objects.first()
  first_restaurant.nickname = "The Cozy Corner"
  first_restaurant.save()

  restaurants_with_name_value_after_update = Restaurant.objects.annotate(
      name_value=Coalesce('nickname', 'name')
  ).values('name_value')
  ```
