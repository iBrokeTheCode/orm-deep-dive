# Django Query Optimization / select_related & prefetch_related / django-debug-toolbar / N+1 Problem

## Covered Concepts

- [Django Debug Toolbar](#django-debug-toolbar)
- [N+1 Problem](#n1-problem)
- [prefetch_related Method](#prefetch_related-method)
- [select_related Method](#select_related-method)
- [only Method](#only-method)
- [Prefetch Objects](#prefetch-objects)

## Reference

### Django Debug Toolbar

Review [documentation](https://django-debug-toolbar.readthedocs.io/en/latest/installation.html)

The basic steps to install and setup it are:

- Install: `python -m pip install django-debug-toolbar`
- Register app

  ```py
  INSTALLED_APPS = [
      # ...
      "debug_toolbar",
      # ...
  ]
  ```

- Add the URLs

  ```py
  from django.urls import include, path
  from debug_toolbar.toolbar import debug_toolbar_urls

  urlpatterns = [
      # ... the rest of your URLconf goes here ...
  ] + debug_toolbar_urls()
  ```

- Add the middleware

  ```py
  MIDDLEWARE = [
      # ...
      "debug_toolbar.middleware.DebugToolbarMiddleware",
      # ...
  ]
  ```

- Configure Internal IPs

  ```py

  INTERNAL_IPS = [
      # ...
      "127.0.0.1",
      # ...
  ]
  ```

### N+1 Problem

The N+1 problem in Django ORM occurs when your application makes more database queries than necessary to fetch related data.

- You make one initial query to get a list of objects (let's say, 'N' objects like restaurants).
- Then, for each of those 'N' objects, your code tries to fetch related information (like ratings for each restaurant) using separate individual queries.
- This results in a total of 1 (initial query) + N (additional queries), hence the name N+1 problem.
- This can lead to performance issues and slow down your application, especially with a large number of related objects.
- Django provides tools like `prefetch_related` and `select_related` to optimize these queries and avoid the N+1 problem

> [!NOTE]
> N+1 Problem is
> In this case, many queries are executed (most of them are very similar and only change the ID)

Update your index view to load restaurants and theirs ratings.

```py
def index(request):
    restaurants = Restaurant.objects.all()

    context = {
        'restaurants': restaurants
    }

    return render(request, 'core/index.html', context)
```

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Home</title>
  </head>
  <body>
    <div>
      {% for restaurant in restaurants %}
      <h3>{{ restaurant.name }}</h3>

      <ul>
        {% for rating in restaurant.ratings.all %}
        <li>{{ rating.rating }}</li>
        {% endfor %}
      </ul>
      {% endfor %}
    </div>
  </body>
</html>
```

### prefetch_related Method

Review [documentation](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#prefetch-related)

> [!TIP]
> With `prefetch_related` the number of queries is reduced to only 2.
> It change the query to **IN** statement.
> From parent to child model (Restaurant > Ratings)
> Suitable for one-to-many (reverse foreign key) and many-to-many.

```py
def index(request):
    restaurants = Restaurant.objects.prefetch_related('ratings')

    context = {
        'restaurants': restaurants
    }

    return render(request, 'core/index.html', context)
```

### select_related Method

Review [documentation](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#select-related)

> [!TIP]
> With `select_related` the number of queries is reduced to only 1.
> It changes the query to **INNER JOIN** statement
> From child to parent model (Rating > Restaurant)
> Suitable for one-to-one and one-to-many

```py
def index(request):
    # ratings = Rating.objects.all()
    ratings = Rating.objects.select_related('restaurant')

    context = {
        'ratings': ratings
    }

    return render(request, 'core/index.html', context)
```

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Home</title>
  </head>
  <body>
    <div>
      {% for rating in ratings %}
      <p>{{ rating.restaurant.name }} - {{ rating.rating }} stars</p>
      {% endfor %}
    </div>
  </body>
</html>
```

### only Method

Review [documentation](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#only)

> [!TIP]
> The `only` method allows us to specify which field retrieve from DB.
> By default all fields are retrieved.

```py
def index(request):
    ratings = Rating.objects.only(
        'rating', 'restaurant__name').select_related('restaurant')

    context = {
        'ratings': ratings
    }

    return render(request, 'core/index.html', context)
```

### Prefetch objects

Review [documentation](https://docs.djangoproject.com/en/5.1/ref/models/querysets/#django.db.models.Prefetch)

```py
from django.db.models import Sum

def index(request):
    # Get all 5-star ratings, and fetch all the sales for restaurants with 5-star ratings.
    restaurants = Restaurant.objects \
        .prefetch_related('ratings', 'sales') \
        .filter(ratings__rating=5) \
        .annotate(total=Sum('sales__income'))

    print(restaurants)

    return render(request, 'core/index.html')
```

The Prefetch object allows us to execute custom logic. For example, without it the query got the total of all sales. By adding the Prefetch object, can also filter and get the total sales of the last month.

```py
def index(request):
    # Get all 5-star ratings, and fetch all the sales for restaurants with 5-star ratings in the last month
    month_ago = timezone.now() - timezone.timedelta(days=30)
    monthly_sales = Prefetch(
        'sales',
        queryset=Sale.objects.filter(datetime__gte=month_ago)
    )

    restaurants = Restaurant.objects.prefetch_related(
        'ratings', monthly_sales).filter(ratings__rating=5)
    restaurants = restaurants.annotate(total=Sum('sales__income'))
    # print([r.total for r in restaurants])
    print([getattr(r, 'total', None) for r in restaurants])

    print(restaurants)

    return render(request, 'core/index.html')
```
