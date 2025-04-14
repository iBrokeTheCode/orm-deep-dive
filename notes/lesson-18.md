# Generic Foreign Keys in Django

## Concepts

### Generic Foreign Keys

**Generic foreign keys** in Django allow a model to establish a foreign key relationship with _any other model_ in the Django application. This is achieved by linking the model to the **content types framework**. These are also referred to as **polymorphic relations**.

### Content Types Framework

The content types framework in Django provides a way to track all the installed models in your application. The central part of this framework is the `ContentType` model.

### `ContentType` Model

The `ContentType` model, provided by Django, allows you to look up any other model in your Django application. A foreign key from your model to the `ContentType` model enables your model to tie itself to any other class in the Django application.

### `GenericForeignKey` Field

The `GenericForeignKey` field is the mechanism for creating these generic relationships. It relies on two other fields in your model:

- A **`ForeignKey` to the `ContentType` model**.
- A **positive integer field (`PositiveIntegerField`)** that stores the primary key of the related object.
  The `GenericForeignKey` field takes references to these two fields as parameters.

### Practical Example: Tagged Item Model

```py
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

class TaggedItem(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
```

In this model:

- `content_type` is a foreign key to the `ContentType` model.
- `object_id` stores the ID of the specific instance of the model we are tagging.
- `content_object` is the `GenericForeignKey` that links to any model instance through `content_type` and `object_id`.

### Practical Example: Comment Model

The `Comment` model can be associated with either a `Restaurant` or a `Rating` model.

```py
# models.py
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

class Comment(models.Model):
    text = models.TextField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveSmallIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return self.text
```

```py
# admin.py
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import Restaurant, Rating, Comment

class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    inlines = [] # Will be added later

class RatingAdmin(admin.ModelAdmin):
    list_display = ['id', 'rating']

class CommentAdmin(admin.ModelAdmin):
    list_display = ['text', 'content_type', 'object_id', 'content_object']

admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(Rating, RatingAdmin)
admin.site.register(Comment, CommentAdmin)
```

After running `python manage.py makemigrations` and `python manage.py migrate`, the `Comment` model can store comments related to either `Restaurant` or `Rating` instances.

### Using Generic Foreign Keys in the Admin Interface

When adding a `Comment` in the Django admin, the `content_type` field allows you to select any registered model, and the `object_id` field requires the primary key of a specific instance of that selected model. The `content_object` field in the admin display shows a user-friendly representation of the linked object.

### Querying with `content_object`

You can access the related object through the `GenericForeignKey` field (`content_object`).

```py
# orm_script.py
from django.contrib.contenttypes.models import ContentType
from core.models import Restaurant, Rating, Comment

def run():
    comments = Comment.objects.all()
    for comment in comments:
        print(comment.content_object) # Chinese 2
        print(type(comment.content_object)) # # <class 'core.models.Restaurant'>
```

Running this script will print the actual `Restaurant` or `Rating` instance that each comment is associated with.

### How Django Resolves `content_object`

Django uses the `content_type` and `object_id` fields behind the scenes to fetch the correct related object when you access the `content_object`. You can manually do this lookup using the `ContentType` model's `get_object_for_this_type()` method.

```py
def run():
    comment = Comment.objects.first()

    ctype = comment.content_type
    print(ctype) # Core | restaurant

    model = ctype.get_object_for_this_type(pk=comment.object_id)
    print(model) # Chinese 2
    print(type(model)) # <class 'core.models.Restaurant'>
```

### Programmatic Creation using `content_object`

You can create objects with generic foreign keys by directly assigning the instance of the related object to the `content_object` field.

```py
# orm_script.py
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from myapp.models import Restaurant, Rating, Comment

def run():
    restaurant = Restaurant.objects.first()
    comment = Comment.objects.create(
        text="Awful restaurant",
        content_object=restaurant
    )
    print(comment)
    print(comment.__dict__)
```

Django automatically populates the `content_type_id` and `object_id` fields based on the assigned `restaurant` instance.

## Reverse Generic Relations with `GenericRelation`

To easily access all `Comment` objects related to a specific `Restaurant` or `Rating` instance, you can define a **`GenericRelation`** on those models.

```py
# models.py
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models

class Restaurant(models.Model):
    # ...
    comments = GenericRelation('Comment') # Added GenericRelation

class Rating(models.Model):
    # ...
    comments = GenericRelation('Comment') # Added GenericRelation
```

Now, you can access comments for a restaurant like this:

```py
# orm_script.py
from django.contrib.contenttypes.models import ContentType
from core.models import Restaurant, Rating, Comment

def run():
    restaurant = Restaurant.objects.get(pk=3)
    comments = restaurant.comments.all()
    print(comments)
```

You can also use methods like `.add()`, `.remove()`, and `.count()` on the `comments` relation, similar to ManyToMany managers.

```py
def run():
    restaurant = Restaurant.objects.get(pk=4)
    restaurant.comments.add(
        Comment.objects.create(text='I change my mind',
                               content_object=restaurant)
    )

    print(restaurant.comments.count())

    last_comment = restaurant.comments.last()
    restaurant.comments.remove(last_comment)

    print(restaurant.comments.count())
```

### `related_query_name`

You can add a `related_query_name` to the `GenericRelation` to use in filtering statements on the related model.

```py
# models.py
class Restaurant(models.Model):
    # ...
    comments = GenericRelation(Comment, related_query_name='restaurant')
    # ...
```

Now you can filter comments based on the related `Restaurant`'s fields:

```py
# orm_script.py
from django.contrib.contenttypes.models import ContentType
from core.models import Restaurant, Rating, Comment

def run():
    comments = Comment.objects.filter(
        restaurant__restaurant_type=Restaurant.TypeChoices.INDIAN)
    print(comments)
```

## Generic Relations in Django Admin (Tabular Inline)

You can add related `Comment` objects directly within the admin interface of the `Restaurant` or `Rating` models using **`GenericTabularInline`**.

```py
# admin.py
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.contenttypes.models import ContentType
from .models import Restaurant, Rating, Comment

class CommentInline(GenericTabularInline):
    model = Comment
    ct_field = 'content_type'
    ct_fk_field = 'object_id'
    max_num = 4 # Maximum number of comment forms to display

class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    inlines = [CommentInline] # Added the inline

class RatingAdmin(admin.ModelAdmin):
    list_display = ['id', 'value']
    inlines = [CommentInline] # Added the inline

class CommentAdmin(admin.ModelAdmin):
    list_display = ['text', 'content_type', 'object_id', 'content_object']

admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(Rating, RatingAdmin)
admin.site.register(Comment, CommentAdmin)
```

This will add an inline formset for adding comments directly when creating or editing `Restaurant` or `Rating` objects in the Django admin.

## Django Permissions System

Django's built-in [permission system](https://docs.djangoproject.com/en/5.2/topics/auth/default/#permissions-and-authorization) utilizes the content types framework and foreign keys to manage permissions for different models. The `Permission` model has a foreign key to the `ContentType` model, linking each permission to a specific model. The `User` and `Group` models have ManyToMany relationships with the `Permission` model, allowing flexible assignment of permissions to users and groups on a per-model basis.
