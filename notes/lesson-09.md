# Django Aggregation & Annotation / values() and values_list() functions

## Covered Concepts

- [Values function on Django QueriySet](#values-function-on-django-queriyset)

## Reference

### Values function on Django QueriySet

- The `values()` function is a method available on Django QuerySets.
- It returns a `QuerySet` that yields **dictionaries** instead of model instances when iterated over.
- Each dictionary in the resulting `QuerySet` represents an object (row) in the database.
- The **keys** in these dictionaries correspond to the **attribute names (fields)** of the model.
- `values()` allows you to select only a **subset of columns** from a database table. This is in contrast to `.all()`, which retrieves all columns by default.
- Using `values()` can be **more performant** than retrieving full model instances, especially when you only need a few fields, as it avoids the overhead of constructing Python model classes.
- Django documentation suggests that `values()` and `values_list()` are generally **safer to use** than `only()` and `defer()` for optimizing field retrieval.
- You can pass **field names as arguments** to the `values()` function to specify which fields you want to retrieve.
- It is possible to fetch fields from **related models** by using the double underscore (`__`) notation to traverse foreign key relationships.
- `values()` can be used with **Django database functions** to perform transformations at the database level (e.g., converting a string to uppercase).

> [!NOTE]
> The `values_list` method work in the same way that `values` method. The difference it's that it return a list of tuples (not a list of dictionaries). When you only retrieve one field, you can use the syntax `values_list('field', flat=True)` to convert the result in a list of str/int/etc. (no more tuples)

- When `values()` is used **before** `annotate()`, it changes how annotations are evaluated. Instead of annotating each original object, the results are **grouped** based on the unique combinations of the fields specified in `values()`, and then the annotation is applied to each unique group.

## Implementation

1.  **Basic Usage:** To retrieve dictionaries containing specific fields, call `values()` on a QuerySet and pass the names of the desired fields as arguments:

    ```python
    restaurants = Restaurant.objects.values('name')
    for restaurant in restaurants:
        print(restaurant) # Output: {'name': 'Restaurant Name'}

    restaurants_with_date = Restaurant.objects.values('name', 'date_open')
    for restaurant in restaurants_with_date:
        print(restaurant) # Output: {'name': 'Restaurant Name', 'date_open': datetime.date(YYYY, MM, DD)}
    ```

    The result is a `QuerySet` of dictionaries.

2.  **Accessing Values:** You can access the values in the returned dictionaries using standard Python dictionary key access:

    ```python
    first_restaurant = Restaurant.objects.values('name').first()
    if first_restaurant:
        print(first_restaurant['name'])
    ```

3.  **Fetching Related Fields:** To retrieve fields from related models, use double underscores (`__`) to follow the foreign key relationship:

    ```python
    ratings = Rating.objects.filter(restaurant__restaurant_type='Italian').values('rating', 'restaurant__name')
    for rating_info in ratings:
        print(f"Rating: {rating_info['rating']}, Restaurant: {rating_info['restaurant__name']}")
    ```

    Here, `restaurant` is the foreign key field on the `Rating` model, and `name` is a field on the `Restaurant` model.

4.  **Using Database Functions:** You can apply database-level functions using keyword arguments in `values()`. Import the function from `django.db.models.functions`:

    ```python
    from django.db.models.functions import Upper

    restaurants_upper_name = Restaurant.objects.values(name_upper=Upper('name'))
    for restaurant in restaurants_upper_name:
        print(restaurant) # Output: {'name_upper': 'RESTAURANT NAME'}
    ```

    The key in the resulting dictionary (`name_upper` in this case) is the keyword argument you provide. The transformation happens in the database.

## Benefits of Using `values()`

- **Performance Improvement:** Reduces the amount of data fetched from the database and the overhead of creating full model instances when only specific fields are needed.
- **Reduced Memory Usage:** When dealing with large datasets, retrieving dictionaries instead of full models can significantly reduce memory consumption.
- **Simplified Data Handling:** For tasks that don't require the full functionality of model instances, working with plain Python dictionaries can be simpler.

# Continues at 14:00

## Interaction with Annotations

When `values()` is called before `annotate()`, the annotation is performed **per unique combination of the values** specified in `values()`. This allows you to perform aggregations and add summary information based on specific groupings:

```python
from django.db.models import Count

restaurant_ratings_count = Restaurant.objects.values('restaurant_type').annotate(num_ratings=Count('rating'))
for item in restaurant_ratings_count:
    print(f"Restaurant Type: {item['restaurant_type']}, Number of Ratings: {item['num_ratings']}")
```

In this example, the results are grouped by `restaurant_type`, and then the number of ratings (`rating` is a ForeignKey to `Restaurant`) is counted for each type.

By using the `values()` function effectively, you can optimize your Django database queries and retrieve data in a format that suits your specific needs.
