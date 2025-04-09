# Django Query Optimization / select_related & prefetch_related / django-debug-toolbar / N+1 Problem

## Covered Concepts

- [Django Debug Toolbar](#django-debug-toolbar)
- [N+1 Problem](#n1-problem)

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
    <ul>
      {% for restaurant in restaurants %}
      <li>{{ restaurant.name }}</li>

      {% for rating in restaurant.ratings.all %}
      <p>{{ rating.rating }}</p>
      {% endfor %} {% endfor %}
    </ul>
  </body>
</html>
```
