# Django Aggregation & Annotation / values() and values_list() functions

## Covered Concepts

- [Values function on Django QueriySet](#values-function-on-django-queriyset)
- [Django Aggregation with `aggregate()`](#django-aggregation-with-aggregate)
- [Annotating models in Django with annotate() method](#annotating-models-in-django-with-annotate-method)

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

#### Implementation

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

#### Benefits of Using `values()`

- **Performance Improvement:** Reduces the amount of data fetched from the database and the overhead of creating full model instances when only specific fields are needed.
- **Reduced Memory Usage:** When dealing with large datasets, retrieving dictionaries instead of full models can significantly reduce memory consumption.
- **Simplified Data Handling:** For tasks that don't require the full functionality of model instances, working with plain Python dictionaries can be simpler.

---

### Django Aggregation with `aggregate()`

In Django applications, it's often necessary to aggregate data to gain insights into your datasets. This involves combining multiple values from multiple rows into a single output value, which is particularly useful for dashboards, reporting applications, and business intelligence software. Django's ORM provides several ways to achieve this, and the `aggregate()` method is a powerful tool for performing complex aggregations.

#### The `aggregate()` Method

The `aggregate()` method is a function defined on Django querysets that allows you to perform aggregation operations over a set of objects. It returns a dictionary containing the results of the aggregations you specify.

**Key Concepts:**

- **Single Output Value:** Aggregation functions, when used with `aggregate()`, condense multiple values into a single summary statistic.
- **Aggregation Functions:** Django provides built-in aggregation functions in the `django.db.models` module, such as:
  - `Count`: Counts the number of objects.
  - `Avg`: Calculates the average value.
  - `Min`: Finds the minimum value.
  - `Max`: Finds the maximum value.
  - `Sum`: Calculates the sum of values.
  - Other functions like `StdDev` (standard deviation) and `Variance` are also available.
- **Dictionary Result:** The `aggregate()` method returns a Python dictionary. The keys of this dictionary are typically derived from the field being aggregated and the aggregation function used (e.g., `id__count`, `rating__avg`), but you can also define custom aliases.
- **Keyword Arguments for Aliases:** You can provide a custom name (alias) for the aggregation result by passing the aggregation as a keyword argument to `aggregate()`. For example, `aggregate(total=Count('id'))` will result in a dictionary with the key `'total'`.
- **Terminal Function:** `aggregate()` is a **terminal operation** on a queryset. This means that once you call `aggregate()`, you cannot chain other queryset methods (like `filter()`, `order_by()`) directly after it. However, you can apply filters to the queryset _before_ calling `aggregate()` to perform aggregations on a subset of the data.
- **Multiple Aggregations:** You can perform multiple aggregations in a single `aggregate()` call by passing multiple keyword arguments, each specifying a different aggregation function (potentially on different fields).

**Examples:**

1.  **Counting all restaurants:**

    ```python
    from django.db.models import Count
    from your_app.models import Restaurant

    total_restaurants = Restaurant.objects.aggregate(total=Count('id'))
    print(total_restaurants)  # Output: {'total': 14} (example value)
    ```

    This example uses the `Count` aggregation function to count the total number of `Restaurant` objects in the database. The result is stored in a dictionary with the key `'total'`.

2.  **Counting restaurants whose name starts with 'c':**

    ```python
    from django.db.models import Count
    from your_app.models import Restaurant

    c_restaurants_count = Restaurant.objects.filter(name__startswith='c').aggregate(count=Count('id'))
    print(c_restaurants_count)  # Output: {'count': 2} (example value)
    ```

    Here, we first filter the `Restaurant` queryset to include only those whose names start with 'c', and then we aggregate the count of these filtered objects.

3.  **Calculating the average rating:**

    ```python
    from django.db.models import Avg
    from your_app.models import Rating

    average_rating = Rating.objects.aggregate(average=Avg('rating'))
    print(average_rating)  # Output: {'average': 3.0} (example value)
    ```

    This calculates the average value of the `rating` field across all `Rating` objects.

4.  **Calculating the minimum and maximum sale income:**

    ```python
    from django.db.models import Min, Max
    from your_app.models import Sale

    income_range = Sale.objects.aggregate(minimum=Min('income'), maximum=Max('income'))
    print(income_range)  # Output: {'minimum': Decimal('5.71'), 'maximum': Decimal('98.89')} (example values)
    ```

    This demonstrates performing multiple aggregations (`Min` and `Max`) on the `income` field of the `Sale` model in a single `aggregate()` call.

5.  **Calculating the sum, average, minimum, and maximum income for recent sales:**

    ```python
    from django.db.models import Avg, Min, Max, Sum
    from django.utils import timezone
    from datetime import timedelta
    from your_app.models import Sale

    one_month_ago = timezone.now() - timedelta(days=31)
    recent_sales_aggregations = Sale.objects.filter(date_time__gte=one_month_ago).aggregate(
        average=Avg('income'),
        minimum=Min('income'),
        maximum=Max('income'),
        total_sum=Sum('income')
    )
    print(recent_sales_aggregations)
    # Output: {'average': 58.0, 'minimum': Decimal('6.91'), 'maximum': Decimal('99.70'), 'total_sum': Decimal('3491.00')} (example values)
    ```

    This example shows how to filter a queryset (sales within the last month) before applying the `aggregate()` method to calculate multiple summary statistics on that filtered data.

---

### Annotating models in Django with annotate() method

**Annotation in Django adds a summary record or some sort of aggregated record for every single model in the queryset**. Rather than a single output number (as with aggregation), annotation enriches each Django model in the queryset with a particular value that is not defined by default on that model. This allows you to add new and important data to your Django models in a queryset.

**Key Differences from Aggregation:**

- **Aggregation:** Breaks down multiple values into a single value. Returns a Python dictionary with the aggregation results.
- **Annotation:** Adds a value to each model in the queryset. The queryset remains, but each model now has an extra attribute.

#### The `annotate()` Method

The `annotate()` method is a function defined on Django querysets that allows you to add extra fields to each object in the queryset. It works similarly to `aggregate()` in that you can pass keyword arguments representing the name of the field you're annotating and the aggregation or database function you're applying.

**Key Concepts and Examples:**

- **Adding the Length of a Field:** You can use database functions like `Length` to add information based on existing fields.

  ```python
  from django.db.models.functions import Length
  from your_app.models import Restaurant

  restaurants = Restaurant.objects.annotate(length_name=Length('name'))
  first_restaurant = restaurants.first()
  print(first_restaurant.length_name) # Output: (length of the first restaurant's name)
  ```

  Here, each `Restaurant` object in the `restaurants` queryset will have a new attribute called `length_name` containing the length of its `name` field.

- **Accessing Annotated Values:** The newly added attribute can be accessed like any other attribute on the model instance.

- **Using `annotate()` with `values()`:** To retrieve only specific fields along with the annotation, you can chain `.values()` after `.annotate()`. This returns a queryset of dictionaries.

  ```python
  restaurants_with_lengths = Restaurant.objects.annotate(length_name=Length('name')).values('name', 'length_name')
  for restaurant_data in restaurants_with_lengths:
      print(restaurant_data) # Output: {'name': '...', 'length_name': ...}
  ```

  This is more efficient if you don't need all the fields of the Django model.

- **Using Database Functions for Transformation:** You can use functions like `Upper` and `Concat` to transform or combine fields during annotation.

  ```python
  from django.db.models.functions import Upper, Concat
  from django.db.models import Value, CharField
  from your_app.models import Restaurant, Rating
  from django.db.models import Avg

  restaurants_with_upper_name = Restaurant.objects.annotate(name_upper=Upper('name')).values('name', 'name_upper')

  restaurants_with_avg_rating_message = Restaurant.objects.annotate(
      message=Concat(
          'name',
          Value(' (rating: ', output_field=CharField()),
          Avg('rating__rating'), # Assuming a reverse relation from Restaurant to Rating
          Value(')', output_field=CharField()),
          output_field=CharField()
      )
  ).values('name', 'message')
  ```

  The first example annotates each restaurant with an uppercase version of its name. The second example (more complex) attempts to concatenate the restaurant name with its average rating.

- **Filtering by Annotations:** You can filter querysets based on the annotated values.

  ```python
  restaurants_long_name = Restaurant.objects.annotate(length_name=Length('name')).filter(length_name__gte=10)
  for restaurant in restaurants_long_name:
      print(restaurant.name, restaurant.length_name)
  ```

  This will return only restaurants whose name has 10 or more characters.

- **Ordering by Annotations:** You can order querysets based on the annotated values.

  ```python
  restaurants_ordered_by_name_length = Restaurant.objects.annotate(length_name=Length('name')).order_by('length_name')
  restaurants_ordered_by_name_length_desc = Restaurant.objects.annotate(length_name=Length('name')).order_by('-length_name')
  ```

  These examples order restaurants by the length of their names in ascending and descending order, respectively.

- **Annotating with Aggregations over Related Models:** You can use aggregation functions like `Count` and `Sum` within `annotate()` to get summary information from related models for each model in the primary queryset.

  ```python
  from django.db.models import Count, Sum
  from your_app.models import Restaurant, Sale, Rating

  restaurants_with_total_sales = Restaurant.objects.annotate(total_sales=Sum('sales__income')) # Assuming a reverse relation from Restaurant to Sale
  for restaurant in restaurants_with_total_sales:
      print(restaurant.name, restaurant.total_sales)

  restaurants_with_num_ratings = Restaurant.objects.annotate(num_ratings=Count('rating')) # Assuming a reverse relation from Restaurant to Rating
  for restaurant_with_ratings in restaurants_with_num_ratings.values('name', 'num_ratings'):
      print(restaurant_with_ratings)
  ```

  The first example annotates each restaurant with the total income from all its associated sales. The second example annotates each restaurant with the number of ratings it has received.

- **Grouping Annotations using `values()` before `annotate()`:** When `.values()` is used before `.annotate()`, the original results are grouped according to the unique combination of fields specified in the `.values()` clause, and the annotation is then provided for each unique group.

  ```python
  restaurant_ratings_by_type = Restaurant.objects.values('restaurant_type').annotate(num_ratings=Count('rating'))
  for item in restaurant_ratings_by_type:
      print(item) # Output: {'restaurant_type': 'Italian', 'num_ratings': 10}, {'restaurant_type': 'Chinese', 'num_ratings': 5}, ...
  ```

  This example calculates the number of ratings for each distinct `restaurant_type`.

- **Aggregating Annotated Values:** You can further aggregate the results of an annotated queryset using the `aggregate()` method.

  ```python
  from django.db.models import Avg

  restaurants_with_low_sales = Restaurant.objects.annotate(total_sales=Sum('sale__income')).filter(total_sales__lt=300)
  average_sales_low_sales = restaurants_with_low_sales.aggregate(average_sales=Avg('total_sales'))
  print(average_sales_low_sales)
  ```

  This calculates the average total sales for restaurants whose total sales are less than 300.
