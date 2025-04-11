# Django Q Objects and Advanced Filtering

Review [documentation](https://docs.djangoproject.com/en/5.1/topics/db/queries/#complex-lookups-with-q-objects)

## Key Concepts:

- **Q Objects for Complex Lookups:** Q objects are used to encapsulate a collection of keyword arguments for database lookups. They allow for more complex query logic than simple keyword arguments passed to `filter()`.
- **OR Conditions:** By default, multiple keyword arguments in `filter()` are combined with a logical `AND`. To perform an `OR` operation, you need to use Q objects and the **`|` (pipe) operator**.
- **AND Conditions with Q Objects:** While the default behavior of `filter()` with multiple keyword arguments is `AND`, you can explicitly use the **`&` (ampersand) operator** to combine Q objects with an `AND` condition.
- **NOT Conditions:** The **`~` (tilde) operator** can be used to negate a Q object, effectively performing a `NOT` operation in the database query.
- **Basic SQL Pattern Matching (`LIKE`):** Django provides lookups like `icontains` and `endswith` that translate to the SQL `LIKE` operator for basic pattern matching.
- **Regular Expression Lookups (`regex`):** For more advanced pattern matching, Django offers the `regex` lookup, which allows you to use regular expressions in your database queries.
- **Encapsulating Query Logic:** Q objects allow you to encapsulate complex query conditions into reusable objects, making your code cleaner and easier to understand.
- **Combining Q Objects:** You can combine multiple Q objects using the logical operators (`|`, `&`, `~`) to build highly specific and complex database queries.
- **Integration with ORM Features:** Q objects work seamlessly with other Django ORM features like `filter()`, `exclude()`, `select_related()`, and `prefetch_related()`.

## Examples:

### 1. Attempting to Filter with Multiple Identical Keyword Arguments (Illustrating the Need for Q Objects for OR):

```python
# This will raise an error in Django
# restaurant.objects.filter(restaurant_type='Italian', restaurant_type='Mexican')
```

**Explanation:** Django disallows using the same field multiple times in `filter()` with standard keyword arguments as it doesn't make logical sense for an `AND` operation.

### 2. Filtering with OR using Q Objects for `restaurant_type`:

```python
from django.db.models import Q

italian = 'Italian'
mexican = 'Mexican'

restaurants = Restaurant.objects.filter(
    Q(restaurant_type=italian) | Q(restaurant_type=mexican)
)
# This generates an SQL query with an OR condition:
# WHERE restaurant_type = 'Italian' OR restaurant_type = 'Mexican'
```

**Explanation:** Two Q objects are created, each encapsulating a condition on the `restaurant_type` field. The **`|` operator** combines them to create an `OR` condition.

### 3. Filtering with `icontains` for Pattern Matching in `name`:

```python
restaurants = Restaurant.objects.filter(name__icontains='1')
# This generates an SQL query using the LIKE operator with wildcards:
# WHERE name LIKE '%1%'
```

**Explanation:** The `icontains` lookup checks if the `name` field contains the specified string ('1' in this case), using the SQL `LIKE` operator with `%` wildcards.

### 4. Filtering with `endswith` for Pattern Matching in `name`:

```python
restaurants = Restaurant.objects.filter(name__endswith='1')
# This generates an SQL query using the LIKE operator with a leading wildcard:
# WHERE name LIKE '%1'
```

**Explanation:** The `endswith` lookup checks if the `name` field ends with the specified string ('1'), using the SQL `LIKE` operator with a leading `%` wildcard.

### 5. Filtering with OR using Q Objects for `name` with `icontains`:

```python
restaurants = Restaurant.objects.filter(
    Q(name__icontains='Italian') | Q(name__icontains='Mexican')
)
# This finds restaurants whose name contains either 'Italian' or 'Mexican'
```

**Explanation:** Similar to the `restaurant_type` example, this uses Q objects and the `|` operator to find restaurants where the `name` field contains either 'Italian' or 'Mexican'.

### 6. Encapsulating OR Condition in a Q Object:

```python
italian_or_mexican = Q(name__icontains='Italian') | Q(name__icontains='Mexican')

# This Q object can now be reused in filter statements
restaurants = Restaurant.objects.filter(italian_or_mexican)
```

**Explanation:** A complex Q object representing the OR condition is created and stored in a variable, making the `filter()` call more readable and the condition reusable.

### 7. Creating a Q Object for a Date Comparison:

```python
from django.utils import timezone
from datetime import timedelta

recently_opened = Q(date_opened__gt=timezone.now() - timedelta(days=40))
```

**Explanation:** This creates a Q object that checks if the `date_opened` field is greater than 40 days ago.

### 8. Combining Multiple Q Objects with OR:

```python
restaurants = Restaurant.objects.filter(italian_or_mexican | recently_opened)
# This finds restaurants whose name contains 'Italian' or 'Mexican' OR were opened in the last 40 days
```

**Explanation:** The previously created `italian_or_mexican` and `recently_opened` Q objects are combined using the `|` operator to create a more complex `OR` query.

### 9. Using the NOT Operator with a Q Object:

```python
not_recently_opened = ~Q(date_opened__gt=timezone.now() - timedelta(days=40))

restaurants = Restaurant.objects.filter(italian_or_mexican | not_recently_opened)
# This finds restaurants whose name contains 'Italian' or 'Mexican' OR were NOT opened in the last 40 days
```

**Explanation:** The `~` operator negates the `recently_opened` Q object, effectively selecting restaurants that were not opened in the last 40 days. This translates to the `NOT` SQL operator.

### 10. Using `regex` Lookup for Numbers in `name` (with `sale` model and foreign key):

```python
name_has_number = Q(restaurant__name__regex=r'[0-9]+')

sales = Sale.objects.filter(name_has_number)
# This finds all sales where the associated restaurant's name contains at least one number.
# The SQL query will use a regular expression operator REGEXP.
```

**Explanation:** The `regex` lookup is used to find restaurant names (accessed via the foreign key `restaurant__name`) that contain one or more digits (`+`). This demonstrates advanced pattern matching using regular expressions in the database.

### 11. Filtering `sale` Objects with OR Condition Using Two Q Objects (`name` has number OR `profit` > `expenditure`):

```python
profited = Q(income__gt=F('expenditure'))

sales = Sale.objects.filter(name_has_number | profited)
# This finds sales where either the associated restaurant's name has a number
# OR the income is greater than the expenditure.
```

**Explanation:** Two Q objects, `name_has_number` and `profited`, are combined with the `|` operator to retrieve sales that satisfy either condition. `F('expenditure')` allows comparison with another field on the same model.

### 12. Demonstrating AND Condition with Q Objects:

```python
sales_with_number_and_profit = Sale.objects.filter(name_has_number & profited)
# This finds sales where the associated restaurant's name has a number
# AND the income is greater than the expenditure.
```

**Explanation:** The `&` operator combines the two Q objects with a logical `AND`, resulting in a more restrictive query.

### 13. Comparing the Count of Results for AND and OR Conditions:

```python
sales_or = Sale.objects.filter(name_has_number | profited)
sales_and = Sale.objects.filter(name_has_number & profited)

print(f"Number of sales with number in name OR profit: {sales_or.count()}")
print(f"Number of sales with number in name AND profit: {sales_and.count()}")
# The AND query is expected to return fewer or an equal number of results compared to the OR query.
```

**Explanation:** This demonstrates the difference in the number of results returned by `OR` and `AND` conditions.

### 14. Using `select_related` with a Filter Using Q Objects:

```python
sales = Sale.objects.filter(name_has_number | profited).select_related('restaurant')
# This will pre-fetch the related Restaurant objects in a single database query,
# improving performance when accessing restaurant information for these sales.
```

**Explanation:** The `select_related('restaurant')` method is chained to the `filter()` call using Q objects to optimize the query by fetching related `Restaurant` objects in the same database query, avoiding multiple database hits.
