# Querying and Creating Records / Working with Foreign Keys

## Covered Concepts

- [RunScript](#runscript)
- [Create records](#create-records)

## Reference

### RunScript

- Review [documentation](https://django-extensions.readthedocs.io/en/latest/runscript.html)
- Create a directory `scripts`

```shell
mkdir scripts
touch scripts/__init__.py
touch scripts/my_script.py
```

- Run the script with the command

```shell
py manage.py runscript my_script
```

### Create Records

```python
from django.utils import timezone
from core.models import Restaurant

def run():
    restaurant = Restaurant()
    restaurant.name = 'My Restaurant'
    restaurant.date_opened = timezone.now()
    restaurant.latitude = -50.25
    restaurant.longitude = -28.75
    restaurant.restaurant_type = Restaurant.TypeChoices.ITALIAN

    restaurant.save()
```
