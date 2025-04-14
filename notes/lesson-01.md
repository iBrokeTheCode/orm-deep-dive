# Django ORM Deep Dive - Introduction to Databases & SQL

## Concepts

- **Django and Relational Databases**: Django is designed to work seamlessly with relational databases, offering excellent tools to query and manipulate data in an object-oriented Pythonic manner through its ORM. While not a strict requirement, database integration is a core strength of the framework.
- **Database Systems**: A database system efficiently stores data and allows querying of database tables to retrieve needed information for applications.
- **Common Database Systems Supported by Django**: Django officially supports several relational database systems:
  - PostgreSQL
  - MariaDB
  - MySQL
  - Oracle
  - SQLite
  - SQLite is a file-based, small, fast, self-contained, highly reliable, and full-featured SQL database engine. It is the most used database engine globally, often built into mobile phones and computers. Django creates an SQLite file (`db.sqlite3`) by default in your project directory upon running migrations.
- **Anatomy of a Database**: A database is a collection of **tables**. Each **table** consists of:
  - **Columns** (or Fields): Represent a specific piece of information you want to store about a particular entity. Each column has a **data type** (e.g., INTEGER, VARCHAR, DATE, REAL).
  - **Rows** (or Records): Represent an observation or a measurement for a particular entity.
- **Primary Keys**:
  - A **primary key (PK)** is a column (or a set of columns in a composite primary key) whose value uniquely identifies each row in a table.
  - Primary key values must be unique within the table.
  - Often, a primary key is an auto-incrementing **ID** field, where the database automatically assigns a unique, sequential integer to each new record.
  - While auto-incrementing IDs are common, other unique identifiers (e.g., Social Security number) can also serve as primary keys.
  - Primary keys are crucial for efficiently querying specific rows.
- **Foreign Keys**:
  - A **foreign key (FK)** is a column in one table that references the primary key of another table.
  - Foreign keys establish relationships between tables, allowing you to join related data.
  - They help reduce data redundancy by storing related information in separate tables and linking them through references rather than duplicating data.
  - For example, a `restaurant_id` in a `rating` table can be a foreign key referencing the `id` (primary key) in a `restaurant` table.
- **SQL (Structured Query Language)**:
  - SQL is the querying language used to interact with relational databases.
  - It allows you to retrieve (SELECT), create, update, and delete records in database tables.

## SQL Examples

Basic SQL commands using a hypothetical restaurant and sales tracking system.

### Selecting Data

- **Selecting all columns and rows from a table**:

  ```sql
  SELECT * FROM core_restaurant;
  ```

  This retrieves all data from the `core_restaurant` table.

- **Filtering rows using the `WHERE` clause**:

  ```sql
  SELECT * FROM core_restaurant WHERE restaurant_type = 'IT';
  ```

  This selects all restaurants where the `restaurant_type` is 'IT' (Italian).

- **Using the `OR` operator for multiple conditions**:

  ```sql
  SELECT * FROM core_restaurant WHERE restaurant_type = 'IT' OR restaurant_type = 'CH';
  ```

  This selects restaurants where the `restaurant_type` is either 'IT' or 'CH' (Chinese).

- **Using the `IN` operator for multiple values in the same column**:

  ```sql
  SELECT * FROM core_restaurant WHERE restaurant_type IN ('IT', 'CH');
  ```

  This achieves the same result as the `OR` example, selecting Italian or Chinese restaurants.

- **Filtering based on date using comparison operators**:

  ```sql
  SELECT * FROM core_restaurant WHERE date_open > '2022-05-01';
  ```

  This selects restaurants that opened after May 1st, 2022.

- **Selecting specific columns**:

  ```sql
  SELECT name FROM core_restaurant WHERE date_open > '2022-05-01';
  ```

  This selects only the `name` of restaurants opened after May 1st, 2022.

  ```sql
  SELECT name, latitude, longitude FROM core_restaurant WHERE date_open > '2022-05-01';
  ```

  This selects the `name`, `latitude`, and `longitude` of restaurants opened after May 1st, 2022.

### Aggregate Functions

- **Calculating the sum of a column**:

  ```sql
  SELECT SUM(income) FROM core_sale;
  ```

  This calculates the total `income` from all records in the `core_sale` table.

- **Calculating the average of a column**:

  ```sql
  SELECT AVG(income) FROM core_sale;
  ```

  This calculates the average `income` from all records in the `core_sale` table.

- **Grouping data using `GROUP BY`**:

  ```sql
  SELECT restaurant_id, SUM(income) FROM core_sale GROUP BY restaurant_id;
  ```

  This calculates the sum of `income` for each `restaurant_id` in the `core_sale` table.

- **Using aliases with `AS` to rename columns in the output**:
  ```sql
  SELECT restaurant_id, SUM(income) AS total_income FROM core_sale GROUP BY restaurant_id;
  ```
  This is the same as the previous example but names the resulting sum column as `total_income`.

### Ordering Data

- **Ordering results using `ORDER BY` (ascending by default)**:

  ```sql
  SELECT restaurant_id, SUM(income) AS total_income FROM core_sale GROUP BY restaurant_id ORDER BY total_income;
  ```

  This orders the results by the `total_income` in ascending order (lowest to highest). Note the use of the alias in the `ORDER BY` clause.

- **Ordering results in descending order using `DESC`**:
  ```sql
  SELECT restaurant_id, SUM(income) AS total_income FROM core_sale GROUP BY restaurant_id ORDER BY total_income DESC;
  ```
  This orders the results by the `total_income` in descending order (highest to lowest).

### Joining Tables

- **Performing an `INNER JOIN` between two tables based on a foreign key relationship**:

  ```sql
  SELECT * FROM core_restaurant INNER JOIN core_sale ON core_restaurant.id = core_sale.restaurant_id;
  ```

  This joins all columns from the `core_restaurant` and `core_sale` tables where the `id` (primary key in `core_restaurant`) matches the `restaurant_id` (foreign key in `core_sale`).

- **Selecting specific columns after a `JOIN`**:

  ```sql
  SELECT core_restaurant.id, core_restaurant.name, core_restaurant.restaurant_type, core_sale.income FROM core_restaurant INNER JOIN core_sale ON core_restaurant.id = core_sale.restaurant_id;
  ```

  This selects specific columns (`id`, `name`, `restaurant_type` from `core_restaurant` and `income` from `core_sale`) after joining the tables.

- **Ordering results after a `JOIN`**:
  ```sql
  SELECT core_restaurant.id, core_restaurant.name, core_restaurant.restaurant_type, core_sale.income FROM core_restaurant INNER JOIN core_sale ON core_restaurant.id = core_sale.restaurant_id ORDER BY core_restaurant.id;
  ```
  This orders the joined results by the `id` from the `core_restaurant` table.

## Django Database Configuration

`DATABASES` setting in Django's `settings.py` file:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

This default configuration sets up an SQLite database for the Django project.

## DB Browser for SQLite

It is recommended to using **DB Browser for SQLite** as a graphical user interface to inspect SQLite database files, view tables, rows, and data, and execute SQL queries.
