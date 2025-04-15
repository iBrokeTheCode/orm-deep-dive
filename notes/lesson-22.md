# Django Model Properties & Methods

## Key Concepts

- **Django Model Classes:** These classes serve as an interface to the data used by your application. They are a useful place to define simple logic related to that data through properties and methods.
- **Model Properties:** These allow you to quickly access derived values from a model instance as if they were fields on the model. They are defined using the **`@property` decorator**.
- **Model Methods:** These define behavior associated with a model instance. Unlike properties, they can take parameters, allowing for comparisons and checks against dynamic values.
- **`get_absolute_url()` Method:** This method is commonly defined in Django models to tell Django how to calculate the URL for a specific object. It is used in the admin interface and whenever a URL for an object is needed.
- **ORM (Object-Relational Mapper):** Django's ORM allows you to interact with your database using Python code and model classes.
- **Derived Values:** Properties are particularly useful for creating values that are calculated based on existing model fields.
- **Handling Nullable Fields:** Properties can provide fallback logic when dealing with fields that can have null values in the database. It is generally recommended to use a default value (like an empty string for `CharField`) instead of `null=True` on character-based fields.
- **Unit Testing:** Model properties and methods are good candidates for writing unit tests to ensure their logic works correctly.
- **Business Logic in Models:** Writing model methods is a valuable technique for keeping business logic close to the data it operates on.
- **`__str__` Method:** This is a magic method that defines the string representation of a model instance.
- **Django URLs and `reverse()`:** Django's URL system maps URLs to views. The `reverse()` function allows you to generate URLs based on their named patterns.
- **Django Views:** These functions handle HTTP requests and return HTTP responses, often rendering templates with data from the models. `get_object_or_404()` is a shortcut to retrieve a single object or return a 404 error if the object is not found. `render()` is used to load a template, populate it with context, and return an `HttpResponse` object.
- **Django Templates:** These are text files that define the structure and presentation of your application's user interface. They can include Django Template Language (DTL) for dynamic content.

## Model Properties

Model properties allow you to access derived values as if they were model fields. This is achieved using the `@property` decorator.

### Example 1: `restaurant_name` Property

This property returns the restaurant's nickname if it's not empty; otherwise, it returns the restaurant's formal name.

```python
from django.db import models

class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    nickname = models.CharField(max_length=100, default='')

    @property
    def restaurant_name(self):
        return self.nickname or self.name
```

> [!NOTE]
> Using `null=True` on `CharField` is not recommended and it's better use `default=''` instead.

### Example 2: Unit Test for `restaurant_name` Property

This demonstrates how to write a unit test for the `restaurant_name` property.

```python
from django.test import TestCase
from .models import Restaurant

class RestaurantTests(TestCase):
    def test_restaurant_name_property(self):
        # Test when nickname is not set (None or empty string after correction)
        restaurant = Restaurant(name="Test Restaurant")
        self.assertEqual(restaurant.restaurant_name, "Test Restaurant")

        # Test when nickname is set
        restaurant.nickname = "Test Nickname"
        self.assertEqual(restaurant.restaurant_name, "Test Nickname")
```

**Explanation:**

- The `@property` decorator allows accessing `restaurant_name` as if it were a field.
- The test instantiates `Restaurant` objects and uses `self.assertEqual` to verify the property's behavior under different conditions.

### Example 3: `was_opened_this_year` Property

This property checks if the restaurant's `date_opened` field's year matches the current year.

```python
from django.db import models
from django.utils import timezone
from datetime import date

class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    date_opened = models.DateField()

    @property
    def was_opened_this_year(self) -> bool:
        current_year = timezone.now().year
        return self.date_opened.year == current_year
```

**Explanation:**

- `timezone.now()` gets the current datetime, and `.year` extracts the year.
- The property compares the year of the `date_opened` field with the `current_year` and returns a boolean.

## Model Methods

Model methods define actions that can be performed on instances of the model. They can accept parameters.

### Example 1: `is_opened_after` Method

This method checks if the restaurant was opened after a specific date provided as an argument.

```python
from django.db import models
from datetime import date

class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    date_opened = models.DateField()

    def is_opened_after(self, target_date: date) -> bool:
        return self.date_opened > target_date
```

**Explanation:**

- The method takes `self` (the instance) and `target_date` (a `date` object) as arguments.
- It compares the `date_opened` of the restaurant instance with the `target_date` and returns `True` if the restaurant was opened after the target date.

## Common Model Methods

Django models often include or benefit from specific methods.

### `__str__` Method

This method provides a human-readable string representation of a model instance.

```python
from django.db import models

class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    # ... other fields ...

    def __str__(self):
        return self.name
```

**Explanation:**

- The `__str__` method in this example returns the `name` of the restaurant.

### `get_absolute_url()` Method

This method defines the canonical URL for accessing a specific instance of the model. It's often used with Django's URL `reverse` function.

**`urls.py` Configuration:**

```python
from django.urls import path
from . import views

urlpatterns = [
    path('restaurant/<int:pk>/', views.restaurant_detail, name='restaurant_detail'),
]
```

**`views.py` Configuration:**

```python
from django.shortcuts import render, get_object_or_404
from .models import Restaurant

def restaurant_detail(request, pk):
    restaurant = get_object_or_404(Restaurant, pk=pk)
    return render(request, 'restaurant.html', {'restaurant': restaurant})
```

**`restaurant.html` Template:**

```html+django
{% extends 'base.html' %}

{% block content %}
    <p>Restaurant ID: {{ restaurant.pk }}</p>
    <p>Restaurant Name: {{ restaurant.name }}</p>
{% endblock %}
```

**`models.py` Implementation:**

```python
from django.db import models
from django.urls import reverse

class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    # ... other fields ...

    def get_absolute_url(self):
        return reverse('restaurant_detail', kwargs={'pk': self.pk})
```

**Explanation:**

- The `reverse('restaurant_detail', kwargs={'pk': self.pk})` part uses the named URL pattern `restaurant_detail` defined in `urls.py`.
- `kwargs={'pk': self.pk}` passes the primary key (`pk`) of the current restaurant instance as a parameter to the URL pattern, allowing Django to generate the specific URL for that restaurant.

**Using `get_absolute_url()` in a Template:**

```html+django
{% for restaurant in restaurants %}
    <p><a href="{{ restaurant.get_absolute_url }}">View {{ restaurant.name }}</a></p>
{% endfor %}
```

**Explanation:**

- In a template, you can call `restaurant.get_absolute_url` to get the URL for each restaurant object and use it in a hyperlink.
