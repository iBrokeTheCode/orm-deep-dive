# Django - select_for_update() Function / Locking Database Rows

- Read `select_for_update` [documentation](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#select-for-update)
- Review the PostgreSQL [Docker image](https://hub.docker.com/_/postgres)
- Read PostgreSQL [documentation](https://www.postgresql.org/)
- Read Django Databases [settings](https://docs.djangoproject.com/en/5.2/ref/settings/#databases)

## Key Concepts

- **Concurrency Issues in Database Transactions:** The video highlights a common problem in web applications where multiple concurrent transactions trying to update the same data can lead to inconsistent states. For example, if two users try to order the last two books in stock simultaneously, and the system reads the stock level before either transaction updates it, both orders might be processed incorrectly, leading to a negative stock count.
- **`select_for_update()` Function:** This Django ORM function is used within a transaction to **lock the rows** returned by a queryset until the end of the transaction. This prevents other concurrent transactions from modifying these locked rows, ensuring data integrity.
- **Atomic Transactions (`transaction.atomic`)**: `select_for_update()` is designed to be used within Django's atomic transactions. An atomic block ensures that all database operations within it are treated as a single unit; they either all succeed (commit) or all fail (rollback).
- **Database Locking Mechanisms:** `select_for_update()` leverages the underlying locking mechanisms provided by the database. It generates the `SELECT FOR UPDATE` SQL statement.
- **Database Support:** While SQLite automatically locks all rows during a transaction, `select_for_update()` is particularly useful in databases like **PostgreSQL, Oracle, and MySQL** that have more granular locking mechanisms.
- **Preventing Race Conditions:** By locking the relevant database rows, `select_for_update()` helps prevent race conditions where multiple transactions read and update data based on stale information.
- **Trade-offs of Locking:** While crucial for data consistency, locking rows can potentially lead to **performance bottlenecks** if many transactions are trying to access and modify the same data, as they might have to wait for locks to be released. Therefore, `select_for_update()` should be used judiciously when strictly necessary.
- **`nowait` Keyword Argument:** When `nowait=True` is passed to `select_for_update()`, if another transaction has already acquired a lock on the selected rows, the query will **immediately raise an error** (`TransactionManagementError`) instead of blocking until the lock is released.
- **`skip_locked` Keyword Argument:** When `skip_locked=True` is passed to `select_for_update()`, the query will **ignore any rows that are currently locked** by other transactions and return only the unlocked rows.

## Examples with Code

### 1. Setting up PostgreSQL with Docker

- **Pulling the PostgreSQL Docker image:**
  ```bash
  docker pull postgres
  ```
- **Running a PostgreSQL container:**
  ```bash
  docker run --name omdb -e POSTGRES_PASSWORD=test -p 5432:5432 -d postgres
  ```
- **Django `settings.py` configuration for PostgreSQL:**
  ```python
  DATABASES = {
      'default': {
          'ENGINE': 'django.db.backends.postgresql',
          'NAME': 'orm_series',
          'USER': 'postgres',
          'PASSWORD': 'test',
          'HOST': 'localhost',
          'PORT': '5432',
      }
  }
  ```
- **Installing the `psycopg2` driver:**
  ```bash
  pip install psycopg2-binary
  ```
- **Creating the database in the PostgreSQL container:**
  ```bash
  docker exec -it <postgres_container_id> createdb -U postgres orm_series
  ```

### 2. Demonstrating Row Locking in the Django Shell

Consider the `Product` model with a `number_in_stock` field. If two users simultaneously order one book each, and the initial `number_in_stock` is 2, without proper locking, both transactions might read the stock as 2, decrement it by 1, and save 1, resulting in a final stock of 1 instead of 0.

While a transaction with `select_for_update()` is active and holding a lock on a `Product` instance, trying to update the same instance in another Django shell session will block until the lock is released.

```python
# Running in one terminal (omm_script.py):
import time
from django.db import transaction
from core.models import Product

with transaction.atomic():
    book = Product.objects.select_for_update().get(name='Book')
    print(f"Book '{book.name}' locked. Sleeping for 60 seconds...")
    time.sleep(60)
    print("Lock released.")

# Running in another terminal (Django shell) while the script above is sleeping:
# python manage.py shell_plus
from core.models import Product
book = Product.objects.get(name='Book')
book.number_in_stock = 10  # This will hang until the lock is released
book.save()
print("Book updated in the shell.")
```

### 3. Using `select_for_update()` to Prevent Concurrency Issues

To solve the concurrency problem, `select_for_update()` is used to lock the `Product` instance before updating its stock:

```python
# views.py (using select_for_update)
from django.shortcuts import render, redirect
from .models import Product, Order
from django.db import transaction
from functools import partial


def order_product(request):
    if request.method == 'POST':
        form = ProductOrderForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                product = Product.objects.select_for_update().get(
                    id=form.cleaned_data['product'].pk
                )

                # simulate
                import time
                time.sleep(25)

                order = form.save()

                order.product.number_in_stock -= order.number_of_items
                product.save()
            transaction.on_commit(partial(email_user, 'example@emai.com'))

            return redirect('core:order_product')
        else:
            return render(request, 'core/order_product.html', {'form': form})

    form = ProductOrderForm()

    context = {
        'form': form
    }

    return render(request, 'core/order_product.html', context)
```

This ensures that once a transaction selects a product using `select_for_update()`, no other transaction can modify that product's row until the first transaction is completed (committed or rolled back).

### 4. Demonstrating the `nowait` Keyword Argument

When `nowait=True` is used, attempting to acquire a lock on a row that is already locked will raise a `TransactionManagementError`:

```python
# Running in one terminal (similar to omm_script.py, sleeping for a longer time)

# Running in another terminal (Django shell):
from django.db import transaction
from core.models import Product

try:
    with transaction.atomic():
        book = Product.objects.select_for_update(nowait=True).get(id=1)
        book.number_in_stock = 4
        book.save()
        print("Book updated.")
except Exception as e:
    print(f"Error updating book: {e}") # This will likely print a TransactionManagementError
```

### 5. Demonstrating the `skip_locked` Keyword Argument

When `skip_locked=True` is used, the query will not return rows that are currently locked:

```python
# Running in one terminal (similar to omm_script.py, holding a lock)

# Running in another terminal (Django shell):
from django.db import transaction
from core.models import Product

try:
    with transaction.atomic():
        # This query will not return the 'Book' instance because it's locked
        book = Product.objects.select_for_update(skip_locked=True).get(id=1)
        product.number_in_stock = 9
        product.save()
except Product.DoesNotExist:
    print("The requested product does not exist (it might be locked and skipped).")
```
