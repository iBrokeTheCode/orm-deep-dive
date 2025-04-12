# Django Database Transactions / atomic() function - BugBytes

- Read PostgreSQL Transaction [documentation](https://www.postgresql.org/docs/current/tutorial-transactions.html)
- Read ACID (Atomic, Constant, Isolated, Durable) [post](https://www.bmc.com/blogs/acid-atomic-consistent-isolated-durable/)

## Concepts

- **Database Transactions:** Transactions bundle multiple database operations into a single **All or Nothing operation**. Intermediate states within a transaction are not visible to other concurrent transactions.

  - If all steps in a transaction complete successfully, the changes are **committed** to the database.
  - If any step fails, a **rollback** occurs, and the database is reverted to its previous state.

- **Atomicity:** This is a key property of transactions, meaning that a transaction is treated as a single, indivisible unit of work. **Either the entire transaction is committed, or no part of it is** (and changes are rolled back). Atomicity is one of the **ACID** properties (Atomic, Consistent, Isolated, Durable) of database transactions.

- **Default Django Behavior (Autocommit):** By default, Django operates in **autocommit mode**. In this mode, each individual database query is automatically wrapped in its own transaction and immediately committed to the database upon successful completion.

- **Commit and Rollback in SQL:**

  ```sql
  BEGIN;
  UPDATE accounts SET balance = balance - 100 WHERE name = 'Alice';
  COMMIT;
  ```

  The `BEGIN` statement starts a transaction. The `UPDATE` statement performs a database modification. The `COMMIT` statement makes the changes permanent.

  ```sql
  BEGIN;
  UPDATE accounts SET balance = balance - 100 WHERE name = 'Alice';
  ROLLBACK;
  ```

  If a `ROLLBACK` statement is issued instead of `COMMIT`, any changes made within the transaction are discarded, and the database returns to its state before the transaction began.

- **`transaction.atomic()`:** Django provides the `atomic()` function in the `django.db.transaction` module to manage transactions explicitly. It ensures the **atomicity** of a block of code involving database operations.

  - If the code within the `atomic()` block executes successfully, the transaction is automatically committed.
  - If an exception occurs within the block, the transaction is automatically rolled back.
  - `atomic()` can be used as either a **decorator** for a function (e.g., a view) or as a **context manager** using the `with` statement.

- **`transaction.on_commit()`:** This function allows you to register **callbacks** that will be executed **after the current open transaction is successfully committed** to the database. This is useful for performing actions that should only occur if the database changes are permanent, such as sending emails after an order is placed.

## Problem Demonstration: Inconsistent Database State without Transactions

We define two models, `Product` and `Order`, to illustrate the need for transactions:

```python
# models.py
from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    number_in_stock = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.name

class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    number_of_items = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"{self.number_of_items} of {self.product.name}"
```

The goal is that when an `Order` is placed, the `number_in_stock` of the corresponding `Product` should be updated accordingly. Without transactions, inconsistencies can arise. For example, an `Order` might be saved, but an error during the stock update could leave the database in an inconsistent state (order recorded, but stock not reduced).

## Initial Attempt to Handle Order Placement (Without Transaction)

We create a `ProductOrderForm`:

```python
# forms.py
from django import forms
from .models import Order

class ProductOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['product', 'number_of_items']
```

And an initial view to handle the form submission:

```python
# views.py
from django.shortcuts import render, redirect
from .forms import ProductOrderForm
from .models import Product, Order

def order_product(request):
    if request.method == 'POST':
        form = ProductOrderForm(request.POST)
        if form.is_valid():
            order = form.save()
            product = order.product
            product.number_in_stock -= order.number_of_items
            product.save()
            return redirect('order_product')
    else:
        form = ProductOrderForm()
    context = {'form': form}
    return render(request, 'order.html', context)
```

This approach has a critical flaw: if the server crashes between saving the `Order` and updating the `Product`'s stock, the database will be inconsistent.

## Adding Validation: `ProductStockException`

A custom exception is defined to handle cases where there isn't enough stock:

```python
# forms.py
class ProductStockException(Exception):
    pass
```

The `save` method of the `ProductOrderForm` is overridden to check stock levels:

```python
# forms.py
from django import forms
from .models import Order
from .models import Product

class ProductStockException(Exception):
    pass

class ProductOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['product', 'number_of_items']

    def save(self, commit=True):
        order = super().save(commit=False)
        if order.product.number_in_stock < order.number_of_items:
            raise ProductStockException(f"Not enough items in stock for the product {order.product.name}")
        if commit:
            order.save()
        return order
```

While this prevents orders with insufficient stock, it doesn't solve the issue of potential inconsistencies due to server crashes during the processing of a valid order.

## Using `transaction.atomic()` to Ensure Atomicity

To ensure that saving the order and updating the product stock happen atomically, we use `transaction.atomic()` as a context manager in the view:

```python
# views.py
from django.shortcuts import render, redirect
from .forms import ProductOrderForm
from .models import Product, Order
from django.db import transaction
import sys

def order_product(request):
    if request.method == 'POST':
        form = ProductOrderForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    order = form.save()
                    product = order.product
                    product.number_in_stock -= order.number_of_items
                    product.save()
                    # Simulate a server crash (for demonstration purposes)
                    # sys.exit(1)
                return redirect('order_product')
            except ProductStockException as e:
                form.add_error(None, str(e))
    else:
        form = ProductOrderForm()
    context = {'form': form}
    return render(request, 'order.html', context)
```

By wrapping the order creation and stock update within `with transaction.atomic():`, we ensure that either both operations succeed and are committed to the database, or if an error occurs (like a server crash or an exception), both are rolled back, maintaining data consistency.

## `atomic_requests` Setting

Django also provides an `ATOMIC_REQUESTS` setting (defaulting to `False`) in your settings file. If set to `True`, it automatically wraps the execution of each Django view in a database transaction. This can be convenient but might not always be the desired behavior for all views.

## Performing Actions After Commit (`transaction.on_commit()`)

We can use `transaction.on_commit()` to execute functions only after a transaction has been successfully committed.

First, define a function to be called after commit:

```python
# views.py
def email_user(email):
    print(f"Dear user, thank you for your order. Sending confirmation to: {email}")
```

Then, within the `transaction.atomic()` block, register this function to be called on commit:

```python
# views.py
from django.shortcuts import render, redirect
from .forms import ProductOrderForm
from .models import Product, Order
from django.db import transaction
import sys
from functools import partial

def email_user(email):
    print(f"Dear user, thank you for your order. Sending confirmation to: {email}")

def order_product(request):
    if request.method == 'POST':
        form = ProductOrderForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    order = form.save()
                    product = order.product
                    product.number_in_stock -= order.number_of_items
                    product.save()
                    transaction.on_commit(partial(email_user, "bugbytes@test.com"))
                return redirect('order_product')
            except ProductStockException as e:
                form.add_error(None, str(e))
    else:
        form = ProductOrderForm()
    context = {'form': form}
    return render(request, 'order.html', context)
```

The `email_user` function will only be executed if the entire transaction within the `atomic()` block is successfully committed to the database. We use `functools.partial` to pass arguments to the callback function. If the transaction rolls back (e.g., due to an exception), the `email_user` function will not be called.

## Further Topics (To be covered in a future video)

- **`select_for_update()`:** This Django queryset function allows locking rows in the database until the end of a transaction, which is useful for preventing race conditions in concurrent transactions. This functionality requires a database that supports row-level locking (not SQLite by default).
