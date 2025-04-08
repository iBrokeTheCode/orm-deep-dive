# Model Field Validators / Writing Custom Validators / ModelForms

## Covered Concepts

- [Django Validators](#django-validators)

## Reference

### Django Validators

Review [documentation](https://docs.djangoproject.com/en/5.2/ref/validators/)

```python
models.py
from django.core.validators import MaxValueValidator, MinValueValidator

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name='ratings')
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
```

> [!WARNING]
> The following statements will create the rating instance (the validators won't be executed)

```python
# orm_script.py
from django.db import connection
from django.contrib.auth.models import User
from pprint import pprint

from core.models import Rating, Restaurant


def run():
    restaurant = Restaurant.objects.first()
    user = User.objects.first()
    Rating.objects.create(
        restaurant=restaurant,
        user=user,
        rating=20
    )

    pprint(connection.queries)
```

> [!TIP]
> This following statements will raise errors (from validators) by using `full_clean` method
> `Call clean_fields(), clean(), validate_unique(), and validate_constraints() on the model. Raise a ValidationError for any errors that occur.`
