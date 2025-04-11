# Django - F Expressions for database-level operations

## Covered Concepts

- [F Expressions in Django](#1-f-expressions-in-django)
- [F Expressions in filter() functions to compare with other column values](#2-f-expressions-in-filter-functions-to-compare-with-other-column-values)
- [F Expressions in Django annotate() function](#3-f-expressions-in-django-annotate-function)
- [F Expressions in Django aggregate() function](#4-f-expressions-in-django-aggregate-function)
- [refresh_from_db() function in Django](#5-refresh_from_db-function-in-django)

## Reference

### 1. F Expressions in Django

Read [documentation](https://docs.djangoproject.com/en/5.2/ref/models/expressions/#f-expressions)

- An **F object** represents the value of a model field, a transformed value of a model field, or an annotated column.
- **Key Benefit:** F expressions enable you to refer to field values and perform database operations using them **without actually having to pull them out of the database and into Python memory**.
- Django uses the F object to generate an **SQL expression** that describes the required operation at the database level.
- This can lead to **better performance** and can **reduce the number of queries** issued and the amount of data pulled into memory.

**Simple Update Example:**

```python
from django.db.models import F
from core.models import Rating

def run():
    rating = Rating.objects.filter(rating=3).first()
    if rating:
        # Instead of:
        # rating.rating += 1
        # rating.save(update_fields=('rating',))

        # Use F expression:
        rating.rating = F('rating') + 1
        rating.save(update_fields=('rating',))

        print(f"Rating before (in Python object): {rating.rating}")
```

In this example, `F('rating') + 1` tells the database to update the `rating` field of the selected record to its current value plus one. This operation happens directly in the database.

**Updating Multiple Records with F Expressions:**

- F expressions are particularly useful for updating multiple records in a queryset efficiently with a single database query.

  ```py
  from django.db.models import F
  from core.models import Restaurant

  def run():
      Restaurant.objects.update(rating=F('rating') * 2)
  ```

  In this example, `Restaurant.objects.all().update(rating=F('rating') * 2)` uses an F expression to multiply the current value of the `rating` field by two for **every** `Restaurant` object in the database. This is done at the database level with a single `UPDATE` statement, making it more performant than pulling these values all out into memory and then issuing an update for each row in the table.

**Illustrative Example with `bulk_update()`:**

- Add a new `expenditure` field to the `Sale` model. It then populates this field with random values for all `Sale` objects and uses `bulk_update()` to save these changes to the database efficiently. While this specific example doesn't directly use an F expression _within_ the `bulk_update()` call, it sets the stage for scenarios where you might calculate values based on existing fields (potentially using F expressions in Python before the `bulk_update()` call).

  ```py
  import random
  from your_app.models import Sale

  def run():
    sales = Sale.objects.all()
    for sale in sales:
        from decimal import Decimal
        sale.expenditure = Decimal(random.uniform(5, 100))
    Sale.objects.bulk_update(sales, ['expenditure'])

    print("Expenditures updated with random values using bulk_update.")
  ```

> [!NOTE]
> The `bulk_update()` method, is primarily used for updating multiple existing model instances that you have already fetched and modified in Python. You prepare a list of model objects with their new attribute values in Python and then pass this list to `bulk_update()`, along with the fields that need to be updated. The key advantage of `bulk_update()` is that it performs the updates for all the provided objects in a single database query, making it significantly more efficient than calling the `save()` method on each object in a loop

### 2. F Expressions in `filter()` Functions to Compare with Other Column Values

- F expressions can be used within `filter()` to **compare the values of one model field with another field on the same model**.
- This comparison happens at the database level, which is more efficient than fetching all objects and performing the comparison in Python.

  ```py
  from django.db.models import F
  from your_app.models import Sale

  def run():
      sales_with_loss = Sale.objects.filter(expenditure__gt=F('income'))
      for sale in sales_with_loss:
          print(f"Sale ID: {sale.id}, Income: {sale.income}, Expenditure: {sale.expenditure}")
      print(f"Number of sales with loss: {sales_with_loss.count()}")
  ```

  Here, `expenditure__gt=F('income')` filters the `Sale` objects to find those where the value in the `expenditure` field is greater than the value in the `income` field.

### 3. F Expressions in Django `annotate()` Function

- F expressions can be used with the `annotate()` function to **add dynamic, calculated fields to your query results**.
- The calculation is performed at the database level.
- **Example: Annotating each sale with its profit (income - expenditure)**

  ```python
  from django.db.models import F
  from django.db.models import DecimalField
  from your_app.models import Sale

  def run():
    sales = Sale.objects.annotate(profit=F('income') - F('expenditure'))
    first_sale = sales.values('income', 'expenditure', 'profit').first()
    if first_sale:
        print(first_sale['income'])
        print(first_sale['expenditure'])
        print(first_sale['profit'])
    else:
        print("No sales records found.")

    sales = Sale.objects.annotate(profit=F('income') - F('expenditure'))
    first = sales.values('profit', 'expenditure',
                         'income').order_by('-profit').first()

    if first:
        print(first.get('profit'))
  ```

  In this example, `Sale.objects.annotate(profit=F('income') - F('expenditure'))` adds a `profit` attribute to each `Sale` object in the queryset, calculated by subtracting the `expenditure` field's value from the `income` field's value.

### 4. F Expressions in Django `aggregate()` Function

- F expressions can be used within the `aggregate()` function, often in conjunction with **Q objects and aggregation functions like `Count`**, to perform conditional aggregations based on comparisons between fields.
- **Example: Counting the number of sales with profit and loss**

  ```python
  from django.db.models import F, Count, Q
  from django.db.models import DecimalField
  from your_app.models import Sale

  def run():
      profit_and_loss_counts = Sale.objects.aggregate(
          profit=Count('id', filter=Q(income__gt=F('expenditure'))),
          loss=Count('id', filter=Q(income__lt=F('expenditure'))),
      )
      print(f"Number of sales with profit: {profit_and_loss_counts['profit']}")
      print(f"Number of sales with loss: {profit_and_loss_counts['loss']}")
  ```

  Here, we use `aggregate()` with `Count` and `Q` objects. The filters `Q(income__gt=F('expenditure'))` and `Q(income__lt=F('expenditure'))` use F expressions to compare the `income` and `expenditure` fields at the database level before counting the number of sales that meet each condition.

### 5. `refresh_from_db()` Function in Django

- When you use an F expression to update a field and then immediately try to access that field's value on the same model instance in your Python code, you **might not see the updated value immediately**.
- This is because the update happens at the database level, and the Python object in memory is not automatically refreshed. The attribute might appear as a `CombinedExpression` object.
- To get the latest value from the database into your model instance, you need to call the **`refresh_from_db()`** method.
- **Example (continued from the Simple Update Example):**

  ```python
  from django.db.models import F
  from your_app.models import Rating

  def run():
      rating = Rating.objects.filter(rating=3).first()
      if rating:
          rating.rating = F('rating') + 1
          rating.save()
          print(f"Rating before refresh: {rating.rating}") # Output might be <CombinedExpression: F(rating) + Value(1)>
          rating.refresh_from_db()
          print(f"Rating after refresh: {rating.rating}") # Output will be the updated value from the database
  ```

  Calling `rating.refresh_from_db()` fetches the latest state of the `rating` object from the database, ensuring that `rating.rating` now reflects the updated value. This is important if you need to reuse the model instance with the updated value or perform further saves on it in the same request.
