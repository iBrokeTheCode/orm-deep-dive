# Django Subqueries, OuterRef, and Exists Objects

- Read [documentation](https://docs.djangoproject.com/en/5.2/ref/models/expressions/#subquery-expressions)
- Read [documentation](https://docs.djangoproject.com/en/5.2/ref/models/expressions/#exists-subqueries)

## Key Concepts

- **Subqueries**: A complete SELECT command enclosed in parentheses and used within another SQL command (SELECT, UPDATE, INSERT, or DELETE).
- **`Subquery` Expression**: Allows you to add a subquery to an existing Django queryset.
- **`OuterRef` Expression**: Used when a subquery needs to refer to a field that exists in the outer query. It acts similarly to an `F` object but refers to a column in the outer query.
- **`Exists` Object**: A subclass of `Subquery` that translates to the SQL `EXISTS` statement. It checks for the existence of rows matching a subquery and often performs better than a regular subquery in such cases. It returns a Boolean value.
- **Annotating with Subqueries**: Adding extra information (fields) to a queryset based on the results of a subquery.
- **Filtering with Subqueries**: Using subqueries within the `where` clause to filter the results of a main query.

## Examples

### 1. Filtering Sales for Italian and Chinese Restaurants (Simple Django Filter)

This example demonstrates a simple way to filter sales for restaurants of specific types without explicitly using the `Subquery` object.

```python
sales = Sale.objects.filter(restaurant__restaurant_type__in=['IN', 'IT'])
print(len(sales))
print(sales.values_list('restaurant__restaurant_type', flat=True).distinct())
```

This code filters the `Sale` model to include only sales where the related `Restaurant`'s `restaurant_type` is either 'IT' (Italian) or 'CH' (Chinese).

### 2. Filtering Sales for Italian and Chinese Restaurants (Using `Subquery`)

This example shows how to achieve the same result as above but using a subquery.

```python
restaurants = Restaurant.objects.filter(restaurant_type__in=['IT', 'CH']).values('pk')
sales = sale.objects.filter(restaurant__in=Subquery(restaurants))
print(len(sales))
```

Here, a subquery is first created to get the primary keys of all Italian and Chinese restaurants. Then, the `Sale` model is filtered to include sales where the `restaurant` foreign key's value is in the result of this subquery.

### 3. Annotating Restaurants with the Income of Their Most Recent Sale

This example demonstrates how to annotate each restaurant with the income from its most recent sale using `Subquery` and `OuterRef`.

```python
from django.db.models import Subquery, OuterRef, F

# Subquery to get the most recent sale's income for each restaurant
recent_sale_income = sale.objects.filter(restaurant=OuterRef('pk')).order_by('-date_time').values('income')[:1]

# Annotate each restaurant with the income of its last sale
restaurants = Restaurant.objects.all().annotate(last_sale_income=Subquery(recent_sale_income))

for restaurant in restaurants:
    print(f"Restaurant ID: {restaurant.pk}, Last Sale Income: {restaurant.last_sale_income}")
```

In this code, the `recent_sale_income` subquery filters sales for the current restaurant (using `OuterRef('pk')`), orders them by `date_time` in descending order, and selects only the `income` of the first (most recent) sale. This subquery is then used to annotate the `Restaurant` queryset with the `last_sale_income`.

### 4. Annotating Restaurants with the Expenditure of Their Most Recent Sale

Building on the previous example, this shows how to annotate with another value from the same subquery structure.

```python
# Subquery to get the most recent sale's expenditure
recent_sale_expenditure = sale.objects.filter(restaurant=OuterRef('pk')).order_by('-date_time').values('expenditure')[:1]

# Annotate restaurants with the expenditure of the last sale
restaurants = Restaurant.objects.all().annotate(
    last_sale_income=Subquery(recent_sale_income),
    last_sale_expenditure=Subquery(recent_sale_expenditure)
)

for restaurant in restaurants:
    print(f"Restaurant ID: {restaurant.pk}, Last Sale Income: {restaurant.last_sale_income}, Last Sale Expenditure: {restaurant.last_sale_expenditure}")
```

A similar subquery `recent_sale_expenditure` is defined to retrieve the `expenditure` of the most recent sale and used in the `annotate` method.

### 5. Annotating Restaurants with Profit Using F Objects

This example demonstrates how to calculate and annotate profit based on the previously annotated income and expenditure using F objects.

```python
from django.db.models import F

restaurants = Restaurant.objects.all().annotate(
    last_sale_income=Subquery(recent_sale_income),
    last_sale_expenditure=Subquery(recent_sale_expenditure),
    profit=F('last_sale_income') - F('last_sale_expenditure')
)

for restaurant in restaurants:
    print(f"Restaurant ID: {restaurant.pk}, Last Sale Income: {restaurant.last_sale_income}, Last Sale Expenditure: {restaurant.last_sale_expenditure}, Profit: {restaurant.profit}")
```

Here, the `F` objects are used to refer to the `last_sale_income` and `last_sale_expenditure` that were annotated in the previous step, allowing for a calculation of `profit`.

### 6. Filtering Restaurants with Sales Income Greater Than a Value (Using `Exists`)

This example shows how to filter restaurants that have at least one sale with an income greater than 85 using the `Exists` object.

```python
from django.db.models import Exists

# Subquery to check if a restaurant has any sale with income > 85
has_high_income_sales = sale.objects.filter(
    restaurant=OuterRef('pk'),
    income__gt=85
)

# Filter restaurants based on the existence of such sales
restaurants = Restaurant.objects.filter(Exists(has_high_income_sales))
print(restaurants.count())
```

The `has_high_income_sales` subquery checks if any sale for the current restaurant (`OuterRef('pk')`) has an `income` greater than 85. The `Exists` object then filters the `Restaurant` queryset to include only those for which this subquery returns true (i.e., at least one such sale exists).

### 7. Filtering Restaurants with at Least One 5-Star Rating (Using `Exists`)

This example demonstrates filtering restaurants based on whether they have at least one rating of 5 stars.

```python
# Subquery to check if a restaurant has a 5-star rating
has_five_star_rating = Rating.objects.filter(
    restaurant=OuterRef('pk'),
    rating=5
)

# Filter restaurants based on the existence of a 5-star rating
restaurants = Restaurant.objects.filter(Exists(has_five_star_rating))
print(restaurants.count())
```

A subquery checks the `Rating` model for ratings of 5 for the current restaurant. `Exists` then filters the `Restaurant` queryset.

### 8. Filtering Restaurants Without Any 5-Star Ratings (Using Negated `Exists`)

This example shows how to find restaurants that do not have any 5-star ratings by negating the `Exists` object.

```python
restaurants = Restaurant.objects.filter(~Exists(has_five_star_rating))
print(restaurants.count())
```

The tilde (`~`) operator negates the `Exists` condition, returning restaurants for which the subquery (checking for a 5-star rating) returns false.

### 9. Filtering Restaurants with Sales in the Last Five Days (Using `Exists`, `OuterRef`, and `timezone.now()`)

This example filters restaurants that have made at least one sale in the last five days.

```python
from django.utils import timezone
from datetime import timedelta

five_days_ago = timezone.now() - timedelta(days=5)

# Subquery to check for sales in the last five days for a restaurant
has_recent_sales = sale.objects.filter(
    restaurant=OuterRef('pk'),
    date_time__gte=five_days_ago
)

# Filter restaurants based on the existence of recent sales
restaurants = Restaurant.objects.filter(Exists(has_recent_sales))
print(restaurants.count())
```

Here, a `timedelta` is used to define a date five days ago. The subquery checks the `Sale` model for sales related to the current restaurant (`OuterRef('pk')`) with a `date_time` greater than or equal to `five_days_ago`. `Exists` filters the restaurants accordingly.
