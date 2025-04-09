# QuerySet Filtering and Lookups / Ordering and Slicing QuerySets

## Covered Concepts

- [Create custom commands](#create-custom-commands)

## Reference

### Create custom commands

- Create the directory `management/commands` in your app
- Django will register a `manage.py` command for each Python module in that directory whose name doesn't begin with an underscore.
- Your command files must define a class `Command` that extends `BaseCommand`
- For more information, review [documentation](https://docs.djangoproject.com/en/5.1/howto/custom-management-commands/)
- In this lesson, we use the [`populate_db.py`](../core/management/commands/populate_db.py) module to populate our database.
- Run the command

```shell
py manage.py populate_db
```
