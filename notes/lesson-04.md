# Model Field Validators / Writing Custom Validators / ModelForms

## Covered Concepts

- [Django Validators](#django-validators)
- [Test with Forms](#test-with-forms)
- [Custom Validators](#custom-validators)

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
> | `Call clean_fields(), clean(), validate_unique(), and validate_constraints() on the model. Raise a ValidationError for any errors that occur.`

### Test with Forms

Create a `ModelForm`

```python
# forms.py
from django import forms

from .models import Rating

# NOTE: It also work with normal forms (not ModelForm). You must pass the validators here
class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ('restaurant', 'user', 'rating')
```

Create a view (also other steps like `urls.py`, templates, etc.)

```python
from django.shortcuts import render

from .forms import RatingForm

def index(request):
    if request.method == 'POST':
        form = RatingForm(request.POST or None)

        if form.is_valid():
            form.save()
        else:
            return render(request, 'core/index.html', {'form': form})
    context = {
        'form': RatingForm()
    }

    return render(request, 'core/index.html', context)
```

> [!WARNING] > `save` method must be used with `ModelForms`. Don't use it in not `ModelForms` (form.cleaned_data)

### Custom Validators

Create a custom validator (function)

```python
# models.py
from django.core.exceptions import ValidationError


def start_with_a_validator(name: str):
    if not name.lower().startswith('a'):
        raise ValidationError('Restaurant name must start with a')
```

Add it to the field

```python
# models.py

# ...
class Restaurant(models.Model):
    name = models.CharField(max_length=100, validators=[
                            start_with_a_validator])
```

Test it with your form

```python
# views.py
def index(request):
    if request.method == 'POST':
        form = RestaurantForm(request.POST or None)

        if form.is_valid():
            print(form.cleaned_data)
        else:
            return render(request, 'core/index.html', {'form': form})
    context = {
        'form': RestaurantForm()
    }

    return render(request, 'core/index.html', context)
```
