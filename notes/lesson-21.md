# Django Proxy Models - Customizing Model Behaviour

- Read [documentation](https://docs.djangoproject.com/en/5.2/topics/db/models/#proxy-models)

## Concepts

- **Definition**: Django proxy models are subclasses of existing Django models that allow you to customize the Python behavior of the model.
- **Purpose**: They are used when you want to change things like the **default model manager** or **add new methods** to a model class without creating a new database table.
- **No Database Table Creation**: Unlike multi-table inheritance, where each subclass creates a new database table, proxy models operate on the **same database table** as their parent model.
- **Python-Level Changes**: Proxy models enable you to modify the Python-level behavior, such as changing the **default model ordering**, **filtering querysets**, or adding **custom methods**.
- **Data Interaction**: You can **create, delete, and update instances** of a proxy model, and all the data is saved to the database as if you were using the original model.
- **`Meta` Class with `proxy = True`**: A proxy model is defined by inheriting from a parent model and setting `proxy = True` within its inner `Meta` class.
- **Use Cases**: Proxy models are useful for **differentiating rows** that share a database table and applying custom behavior based on certain conditions, such as the value of a specific field.

By using proxy models, you can keep your base model clean and generic while adding specialized behavior through these Python-level customizations.

## Examples with Code

### 1. Defining the Base Model (`models.py`)

```python
from django.db import models

class TaskStatus(models.IntegerChoices):
    TODO = 1, 'To-do'
    IN_PROGRESS = 2, 'In progress'
    COMPLETED = 3, 'Completed'

class Task(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=TaskStatus.choices)

    def __str__(self):
        return self.name
```

This code defines a base `Task` model with a `status` field that uses `TaskStatus` as choices.

### 2. Filtering Tasks in a Script (`proxy_models.py`)

```python
from core.models import Task, TaskStatus

# Fetch all tasks that are in progress
in_progress_tasks = Task.objects.filter(status=TaskStatus.IN_PROGRESS)
print("Tasks in progress:")
for task in in_progress_tasks:
    print(task)
```

This script demonstrates how to query the base `Task` model to filter tasks by their status.

### 3. Defining a Proxy Model with a Custom Manager (`models.py`)

```python
from django.db import models

class InProgressTaskManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().filter(status=TaskStatus.IN_PROGRESS)

class InProgressTask(Task):
    objects = InProgressTaskManager()

    class Meta:
        proxy = True
```

Here, `InProgressTask` is a proxy model for `Task`. It defines a custom manager `InProgressTaskManager` that overrides `get_queryset()` to automatically filter for tasks with the `IN_PROGRESS` status.

### 4. Querying the Proxy Model in a Script (`proxy_models.py`)

```python
from core.models import Task, TaskStatus, InProgressTask

# Fetch all in-progress tasks using the proxy model
in_progress = InProgressTask.objects.all()
print("\nIn progress tasks (via proxy model):")
for task in in_progress:
    print(task)
```

This shows how to use the `InProgressTask` proxy model to retrieve only the tasks that are in progress due to the custom manager.

### 5. Defining Proxy Models for Other Statuses (`models.py`)

```python
from django.db import models

class ToDoTaskManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().filter(status=TaskStatus.TODO)

class ToDoTask(Task):
    objects = ToDoTaskManager()

    class Meta:
        proxy = True

class CompletedTaskManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().filter(status=TaskStatus.COMPLETED)

class CompletedTask(Task):
    objects = CompletedTaskManager()

    class Meta:
        proxy = True
```

This extends the concept by creating proxy models for `ToDo` and `Completed` tasks, each with its own custom manager to filter based on their respective statuses.

### 6. Querying All Proxy Models in a Script (`proxy_models.py`)

```python
from core.models import Task, TaskStatus, InProgressTask, ToDoTask, CompletedTask

print("\nIn progress tasks (via InProgressTask proxy model):")
in_progress = InProgressTask.objects.all()
for task in in_progress:
    print(task)

print("\nCompleted tasks (via CompletedTask proxy model):")
completed = CompletedTask.objects.all()
for task in completed:
    print(task)

print("\nTo-do tasks (via ToDoTask proxy model):")
todos = ToDoTask.objects.all()
for task in todos:
    print(task)
```

This script demonstrates querying each of the defined proxy models.

### 7. Setting Custom Ordering in a Proxy Model (`models.py`)

```python
from django.db import models

# ... (TaskStatus and Task models as defined before)

class ToDoTaskManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=TaskStatus.TODO)

class ToDoTask(Task):
    objects = ToDoTaskManager()

    class Meta:
        proxy = True
        ordering = ['created_at'] # Order to-do tasks by creation date
```

The `ToDoTask` proxy model now includes an `ordering` attribute in its `Meta` class, specifying that to-do tasks should be ordered by their `created_at` field.

### 8. Overriding the `save` Method in a Proxy Model (`models.py`)

```python
from django.db import models

# ... (TaskStatus and Task models as defined before)

class InProgressTaskManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=TaskStatus.IN_PROGRESS)

class InProgressTask(Task):
    objects = InProgressTaskManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.status = TaskStatus.IN_PROGRESS
        super().save(*args, **kwargs)

# ... (ToDoTask and CompletedTask models as defined before)
```

The `InProgressTask` proxy model overrides the `save()` method. When a new `InProgressTask` instance is being added to the database (`self._state.adding` is True), its `status` field is automatically set to `TaskStatus.IN_PROGRESS`.

### 9. Creating a Task Using the Proxy Model in a Script (`proxy_models.py`)

```python
from core.models import Task, TaskStatus, InProgressTask

# Create a new in-progress task using the proxy model
new_task = InProgressTask.objects.create(name="Watch Star Wars")
print("\nCreated task via InProgressTask proxy:", new_task)
print("Task status:", new_task.status)
print("Task status display:", new_task.get_status_display())
```

This script demonstrates creating a new task using the `InProgressTask` proxy model. The `status` is automatically set due to the overridden `save()` method. The `.get_status_display()` method is used to get the human-readable name of the choice. (`get\_<field>_display()`)

### 10. Overriding the `__str__` Method in a Proxy Model (`models.py`)

```python
from django.db import models

# ... (TaskStatus, Task, InProgressTask, and ToDoTask models as defined before)

class CompletedTaskManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=TaskStatus.COMPLETED)

class CompletedTask(Task):
    objects = CompletedTaskManager()

    class Meta:
        proxy = True

    def __str__(self):
        return f"{self.name} (Congratulations, you completed this task)"
```

The `CompletedTask` proxy model overrides the `__str__` method to provide a custom string representation for completed tasks.

### 11. Displaying Tasks Using the Overridden `__str__` Method in a Script (`proxy_models.py`)

```python
from core.models import Task, TaskStatus, CompletedTask

print("\nCompleted tasks (via CompletedTask proxy model with custom __str__):")
completed = CompletedTask.objects.all()
for task in completed:
    print(task)
```

This script shows that when printing instances of `CompletedTask`, the custom `__str__` method is used.
