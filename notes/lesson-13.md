# Django Conditional Expressions with Case() and When() Objects

## Concepts

- **Conditional Expressions:** Enable evaluation of conditions for each row in a database table and return a corresponding result expression based on those conditions.
- **`When()` Objects:** Define the **logic of the conditions** within a conditional expression, representing the "if" part of an if/else statement. They take a condition (or multiple conditions) and a `then` keyword argument specifying the return value if the condition is true.
- **`Case()` Objects:** **Encapsulate the conditions** for a query. They take multiple `When()` objects as arguments and an optional `default` keyword argument to specify a value if none of the `When()` conditions are met.
- **Annotation:** Adding a new field to the results of a Django query set. Conditional expressions are often used within `annotate()` to create these new fields based on logic.
- **Aggregation:** Computing summary statistics (like count, average, sum) over a set of database records. Conditional expressions can be used within aggregation functions.
- **Filtering:** Selecting a subset of database records based on specified conditions. Annotated fields created with conditional expressions can be used for filtering.
- **`Q()` Objects:** Used to encapsulate SQL where clauses and can be combined using logical operators (`|` for OR, `&` for AND). They can be used within `When()` conditions for more complex logic.
- **`Value()` Objects:** Allow you to return a raw, non-model field value within a conditional expression.
- **Output Field:** You can specify the data type of the result of a `Case()` expression using the `output_field` argument.

## Examples

### 1. Annotating if a Restaurant is Italian

- **Goal:** Annotate each restaurant with a boolean field `is_italian` indicating if its type is "Italian".
- **Code:**

  ```python
  from django.db.models import Case, When, BooleanField
  from django.db.models import F # implicitly used via field access
  from .models import Restaurant, RestaurantTypeChoices

  italian_type = RestaurantTypeChoices.ITALIAN

  restaurants = Restaurant.objects.annotate(
      is_italian=Case(
          When(restaurant_type=italian_type, then=True),
          default=False,
          output_field=BooleanField()
      )
  )

  for restaurant in restaurants.filter(is_italian=True):
      print(restaurant)
  ```

- **Explanation:**
  - We import `Case` and `When` from `django.db.models`.
  - We define the `italian_type` for comparison.
  - We use `Restaurant.objects.annotate()` to add a new field `is_italian`.
  - The `Case()` expression checks each restaurant's `restaurant_type`.
  - The `When()` object specifies that if `restaurant_type` is equal to `italian_type`, then the `is_italian` field should be `True`.
  - The `default=False` argument ensures that if the condition in `When()` is not met, `is_italian` will be `False`.
  - `output_field=BooleanField()` specifies the data type of the annotated field.
  - Finally, we filter the restaurants to show only those where `is_italian` is `True`.
- **Corresponding SQL (as seen via `connection.queries`):**
  ```sql
  SELECT ...,
         CASE
             WHEN restaurant.restaurant_type = 'italian' THEN 1
             ELSE 0
         END AS is_italian
  FROM restaurant
  WHERE CASE
            WHEN restaurant.restaurant_type = 'italian' THEN 1
            ELSE 0
        END = 1
  ```
  The `CASE WHEN` SQL construct directly implements the conditional logic defined in the Django ORM.

### 2. Annotating Popular Restaurants Based on Sales Count

- **Goal:** First, annotate each restaurant with the `num_sales`, then annotate with `is_popular` if `num_sales` is greater than 8.
- **Code:**

  ```python
  from django.db.models import Count, Case, When, BooleanField

  restaurants = Restaurant.objects.annotate(
      num_sales=Count('sales')
  ).annotate(
      is_popular=Case(
          When(num_sales__gt=8, then=True),
          default=False,
          output_field=BooleanField()
      )
  )

  for restaurant in restaurants.filter(is_popular=True):
      print(f"{restaurant} (Sales: {restaurant.num_sales})")
  ```

- **Explanation:**
  - We first annotate restaurants with the `num_sales` by counting the related `sales`. The related name `sales` comes from the foreign key relationship in the `Sale` model.
  - Then, we perform a second annotation to add the `is_popular` field.
  - The `Case()` expression checks if the previously annotated `num_sales` field is greater than 8. We access the annotated field directly.
  - If `num_sales` is greater than 8, `is_popular` is set to `True`; otherwise, it defaults to `False`.
  - Finally, we filter and print the restaurants deemed "popular".

### 3. Annotating Restaurants as "Highly Rated" Based on Average Rating and Number of Ratings

- **Goal:** Annotate restaurants as "highly rated" if their average rating is greater than 3.5 AND they have more than one rating.
- **Code:**

  ```python
  from django.db.models import Avg, Count, Case, When, BooleanField

  restaurants = Restaurant.objects.annotate(
      average_rating=Avg('ratings__rating'),
      num_ratings=Count('ratings')
  ).annotate(
      highly_rated=Case(
          When(average_rating__gt=3.5, num_ratings__gt=1, then=True),
          default=False,
          output_field=BooleanField()
      )
  )

  for restaurant in restaurants.filter(highly_rated=True):
      print(f"{restaurant} (Avg Rating: {restaurant.average_rating}, Num Ratings: {restaurant.num_ratings})")
  ```

- **Explanation:**
  - We first annotate each restaurant with its `average_rating` (calculating the average of the `rating` field in the related `Rating` model) and `num_ratings` (counting the related `Rating` objects). The related name `ratings` comes from the foreign key in the `Rating` model.
  - In the second annotation, the `When()` object now takes **two conditions** separated by a comma. **Both conditions must be true** for the `then=True` to be executed.
  - The conditions check if `average_rating` is greater than 3.5 AND `num_ratings` is greater than 1.
  - The `default=False` applies if either or both conditions are false.

### 4. Categorizing Restaurants into Rating Buckets

- **Goal:** Annotate restaurants with a `rating_bucket` field categorized as "highly rated", "average rating", or "bad rating" based on their average rating.
- **Code:**

  ```python
  from django.db.models import Avg, Case, When, Value, CharField

  restaurants = Restaurant.objects.annotate(
      average_rating=Avg('ratings__rating')
  ).annotate(
      rating_bucket=Case(
          When(average_rating__gt=3.5, then=Value('highly rated')),
          When(average_rating__range=(2.5, 3.5), then=Value('average rating')),
          When(average_rating__lt=2.5, then=Value('bad rating')),
          output_field=CharField()
      )
  )

  for restaurant in restaurants.filter(rating_bucket='highly rated'):
      print(f"{restaurant} (Rating Bucket: {restaurant.rating_bucket}, Avg Rating: {restaurant.average_rating})")
  ```

- **Explanation:**
  - We first annotate with `average_rating` as before.
  - The `rating_bucket` annotation uses a `Case()` expression with **multiple `When()` objects**. The conditions are evaluated in order. The first `When()` whose condition is met will have its `then` value returned.
  - We use `Value()` objects to return string literals for the different rating buckets.
  - The `average_rating__range=(2.5, 3.5)` lookup is **inclusive**.
  - We specify `output_field=CharField()` because the `Case()` expression now returns string values. **It's important that all `then` values within a `Case()` expression have a consistent data type (or you specify the output field appropriately)**. The `default` argument is not needed here as the `When` conditions cover all possibilities.

### 5. Assigning Continents to Restaurants Based on Type Using `Q()` Objects

- **Goal:** Annotate restaurants with a `continent` based on their `restaurant_type` (e.g., Italian and Greek are in Europe, Indian and Chinese are in Asia, Mexican is in North America).
- **Code:**

  ```python
  from django.db.models import Case, When, Value, CharField, Q
  from .models import Restaurant, RestaurantTypeChoices

  types = RestaurantTypeChoices()

  european = Q(restaurant_type=types.ITALIAN) | Q(restaurant_type=types.GREEK)
  asian = Q(restaurant_type=types.INDIAN) | Q(restaurant_type=types.CHINESE)
  north_american = Q(restaurant_type=types.MEXICAN)

  restaurants = Restaurant.objects.annotate(
      continent=Case(
          When(european, then=Value('Europe')),
          When(asian, then=Value('Asia')),
          When(north_american, then=Value('North America')),
          default=Value('Not Available'),
          output_field=CharField()
      )
  )

  for restaurant in restaurants.filter(continent='Asia'):
      print(f"{restaurant} (Continent: {restaurant.continent})")
  ```

- **Explanation:**
  - We import `Q` objects from `django.db.models`.
  - We create `Q()` objects to represent the conditions for each continent. The `|` operator performs a logical OR.
  - These `Q()` objects are then used directly as the first argument to the `When()` objects, making the code more readable.
  - We use `Value()` to assign the continent names as string literals.
  - A `default=Value('Not Available')` is provided for restaurant types that don't match any of the `When()` conditions.
  - `output_field=CharField()` is specified for the `continent` field.

### 6. Aggregating Sales Over 10-Day Windows

- **Goal:** Annotate sales data to group total income for each 10-day period.
- **Code:**

  ```python
  from django.db.models import Min, Max, Sum, Case, When, Value, CharField
  from django.db.models import F
  from django.utils import timezone
  from itertools import count

  first_sale = Sale.objects.aggregate(Min('date_time'))['date_time__min']
  last_sale = Sale.objects.aggregate(Max('date_time'))['date_time__max']

  dates = []
  counter = count(0)
  dt = first_sale
  if first_sale and last_sale:
      while dt <= last_sale:
          dates.append(dt.date())
          dt = first_sale + timezone.timedelta(days=10 * next(counter))

  wins = [
      When(
          date_time__range=(date, date + timezone.timedelta(days=10)),
          then=Value(date.strftime('%Y-%m-%d'))
      )
      for date in dates
  ]

  case = Case(*wins, output_field=CharField())

  sales_by_date_range = Sale.objects.annotate(
      date_range=case
  ).values('date_range').annotate(total_sales=Sum('income')).order_by('date_range')

  for item in sales_by_date_range:
      print(f"Date Range: {item['date_range']}, Total Sales: {item['total_sales']}")
  ```

- **Explanation:**
  - We first find the minimum (`first_sale`) and maximum (`last_sale`) dates from the `Sale` model.
  - We generate a list of dates (`dates`) with 10-day intervals starting from `first_sale` up to `last_sale` using `itertools.count` and `timezone.timedelta`.
  - We create a list comprehension `wins` that generates a `When()` object for each date in our `dates` list. Each `When()` checks if the `date_time` of a sale falls within a 10-day range starting from that date. If it does, it returns the starting date as a string.
  - We create a `Case()` expression by unpacking the `wins` list using `*wins`. The `output_field` is set to `CharField()`.
  - We annotate the `Sale` objects with the `date_range` using our `Case()` expression.
  - Finally, we group the sales by `date_range` using `.values('date_range')` and calculate the `total_sales` for each range using `Sum('income')`.

This README provides a comprehensive overview of Django conditional expressions using `Case()` and `When()` as explained in the BugBytes video, along with detailed code examples. Remember to adapt the model and field names to your specific Django project.
