# Django Database Constraints Explained

## Concepts

A **database constraint** is a restriction or a limitation on the possible values that can be entered into a particular column or a combination of columns in a database table. Database constraints are crucial for maintaining data integrity and consistency.

- **Primary Key Constraint**: Uniquely identifies each row in a table. Typically a single column with an auto-incrementing integer or a UUID.
- **Check Constraint**: Defines a condition that must be true for all values in a column. Ensures data within a specific range or format.
- **Unique Constraint**: Ensures that all values in a column or a group of columns are different. Automatically creates a database index for efficient data retrieval.
- **Not Null Constraint**: Prevents null values from being entered into a column. In Django, fields are `NOT NULL` by default unless `null=True` is specified.
- **Foreign Key Constraint**: Establishes a link between two tables, ensuring referential integrity. Values in the foreign key column must correspond to values in the primary key column of another table.
- **Default Values**: Specifies a value that will be automatically assigned to a column if no value is provided during insertion.

## Applying Constraints in Django Models

Django allows you to define database constraints programmatically through your model definitions. This ensures that data validation happens at the database level, regardless of how data is being entered into the database (e.g., through Django forms, shell commands, or other applications).

### Automatic Constraints from Django Field Types

Certain Django model fields implicitly create database constraints. For example, a `PositiveSmallIntegerField` in Django automatically creates a **check constraint** in the database to ensure that the value is greater than or equal to zero.

**Example:**

```py
from django.db import models

class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    capacity = models.PositiveSmallIntegerField() # Creates a check constraint (capacity >= 0)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    website = models.URLField(blank=True, null=True)
```

The SQL representation (in SQLite) of the `capacity` field shows the automatically created check constraint:

```sql
CREATE TABLE core_restaurant (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    capacity SMALLINT UNSIGNED CHECK (capacity >= 0) NOT NULL,
    latitude DECIMAL NOT NULL,
    longitude DECIMAL NOT NULL,
    website TEXT
)
```

### Explicitly Defining Check Constraints

You can define custom check constraints in your Django models using the `CheckConstraint` object within the `Meta` class of your model. This allows you to enforce specific conditions on your model fields at the database level.

**Example (Rating Model):**

```py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Q

class Rating(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(rating__gte=1) & Q(rating__lte=5),
                name='rating_value_valid',
                violation_error_message='Rating invalid. It must fall between 1 and 5'
            )
        ]
```

In this example, a `CheckConstraint` named `rating_value_valid` is added to the `Rating` model. It uses a `Q` object to define the condition that the `rating` field must be greater than or equal to 1 and less than or equal to 5. The `violation_error_message` will be displayed if this constraint is violated.

**Enforcement:** Check constraints are enforced at the database level. If you attempt to save a model instance with a value that violates the constraint, an `IntegrityError` will be raised. You need to run `python manage.py makemigrations` and `python manage.py migrate` to apply these constraints to your database schema.

**Example (Restaurant Model - Latitude and Longitude):**

```py
from django.db import models
from django.db.models import Q

class Restaurant(models.Model):
    # ... other fields ...
    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(latitude__gte=-90) & Q(latitude__lte=90),
                name='valid_latitude'
            ),
            models.CheckConstraint(
                check=Q(longitude__gte=-180) & Q(longitude__lte=180),
                name='valid_longitude'
            )
        ]
```

This example adds check constraints to the `Restaurant` model to ensure that the `latitude` and `longitude` values fall within their valid ranges.

### Explicitly Defining Unique Constraints

You can ensure uniqueness of values in one or more columns using unique constraints. Django provides two main ways to define unique constraints.

**1. Using `unique=True` in Model Fields:**

For simple unique constraints on a single field, you can set the `unique` attribute to `True` in your model field definition.

**Example (Restaurant Model - Name):**

```py
from django.db import models

class Restaurant(models.Model):
    name = models.CharField(max_length=100, unique=True) # Ensures restaurant names are unique
    # ... other fields ...
```

Setting `unique=True` on the `name` field will prevent multiple restaurants from having the same name in the database. This creates a unique index on the `name` column in the database.

**Enforcement:** Attempting to create or update a model instance with a non-unique value for a field with `unique=True` will raise an `IntegrityError` at the database level. You need to run migrations to apply this change.

**2. Using `UniqueConstraint` in the `Meta` Class:**

For more complex unique constraints involving one or more fields, or when you need to apply expressions, you can use the `UniqueConstraint` object within the `Meta` class of your model.

**Example (Restaurant Model - Case-Insensitive Unique Name):**

```py
from django.db import models
from django.db.models.functions import Lower
from django.db.models import UniqueConstraint

class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    # ... other fields ...

    class Meta:
        constraints = [
            UniqueConstraint(Lower('name'), name='restaurant_name_unique_insensitive')
        ]
```

In this example, a `UniqueConstraint` is defined on the lowercase version of the `name` field using the `Lower()` function. This ensures that restaurant names are unique regardless of their case.

**Example (Rating Model - Unique Rating per User per Restaurant):**

```py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Q, UniqueConstraint

class Rating(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(rating__gte=1) & Q(rating__lte=5),
                name='rating_value_valid',
                violation_error_message='Rating invalid. It must fall between 1 and 5'
            ),
            UniqueConstraint(fields=['user', 'restaurant'], name='user_restaurant_unique')
        ]
```

This example adds a `UniqueConstraint` on the combination of the `user` and `restaurant` fields in the `Rating` model. This prevents a single user from submitting multiple ratings for the same restaurant.

**Enforcement:** Similar to check constraints, unique constraints are enforced at the database level, and violating them will result in an `IntegrityError`. You need to run migrations to apply these constraints. If existing data violates a newly added unique constraint, the `migrate` command will fail. You would need to resolve the data inconsistencies before applying the migration.

## Django Model Validators vs. Database Constraints

It's important to distinguish between Django model validators and database constraints.

- **Django Model Validators**: These are functions that are run when you save a model instance through Django's ORM or when processing Django forms. They are useful for providing feedback to users in forms. However, they are not enforced at the database level if data is inserted directly through SQL or other means.
- **Database Constraints**: These are rules enforced directly by the database management system. They ensure data integrity regardless of how data is entered into the database.

For robust data validation, it's recommended to use both Django model validators for user feedback and database constraints for guaranteed data integrity.
