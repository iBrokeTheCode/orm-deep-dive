# Django ER Diagram Generator

- Read about [Entity Relationship Diagram](https://www.lucidchart.com/pages/er-diagrams)
- Review all Django-extensions [Command Extensions](https://django-extensions.readthedocs.io/en/latest/command_extensions.html)
- Review Graph Models [documentation](https://django-extensions.readthedocs.io/en/latest/graph_models.html)
- [Graphviz Online tool](https://dreampuf.github.io/GraphvizOnline/?engine=dot)

## What are ER Diagrams?

**Entity-Relationship (ER) diagrams** are a type of flowchart that illustrates how **entities** (such as people, objects, or concepts) relate to each other within a system. In the context of databases, these entities typically map to **database tables**. ER diagrams are most often used to **design or debug relational databases**.

A typical ER diagram shows:

- **Entities**: Represented by rectangles, corresponding to database tables (e.g., `hockey team`).
- **Fields/Attributes**: Information about the columns within each table (e.g., `ID`, `name`, `logo` in the `hockey team` table). Sometimes, the **data types** of these fields are also visible.
- **Relationships**: Connections between entities, indicating how they are linked (e.g., a `hockey team` is linked to a `hockey game` through a foreign key `team_id`). These relationships can be **one-to-one**, **one-to-many**, or **many-to-many**.

## Generating ER Diagrams with Django Extensions

Use the `graph_models` command from the **Django extensions** package to generate ER diagrams from Django models.

### Installation

Ensure you have `django-extensions` installed. If not, you can install it using pip:

```bash
pip install django-extensions
```

Add `'django_extensions'` to your `INSTALLED_APPS` in your `settings.py` file.

### The `graph_models` Command

The `graph_models` command in `django-extensions` renders a graphical overview of your project or specified applications' models. It generates a **`.dot` file**, which contains code in the DOT language that describes the graph structure. This `.dot` file can then be used by tools like **Graphviz** or online Graphviz generators to create the visual ER diagram.

**Basic Usage Example:**

To generate an ER diagram for the models in a specific application (e.g., `core`), navigate to your project's root directory (where `manage.py` is located) and run the following command:

```bash
python manage.py graph_models core > models.dot
```

This command will create a file named `models.dot` containing the graph description of your `core` application's models.

**Visualizing the `.dot` File:**

Uses an online **Graphviz generator** where you can paste the content of the `models.dot` file to generate the ER diagram visually. The generated diagram will show the entities (e.g., `Restaurant`, `Sale`), their fields (e.g., `income`, `expenditure` in `Sale`), and the relationships between them (e.g., `Sale` having a foreign key to `Restaurant`).

**Including Django's `auth` models:**

To include models from other applications, like Django's built-in `auth` application which contains the `User` model, you can specify them in the command:

```bash
python manage.py graph_models core auth > models.dot
```

This will include the `User`, `Group`, and `Permission` models in the generated ER diagram, showing their relationships with your application's models (e.g., the `Rating` model's foreign key to `User`).

### Django Extensions Settings for `graph_models`

You can configure the `graph_models` command using the `GRAPH_MODELS` setting in your `settings.py` file.

- **`all_applications`**: Set this to `True` to generate an ER diagram for all applications in your project.

  ```python
  GRAPH_MODELS = {
      'all_applications': True,
  }
  ```

- **`app_labels`**: Provide a list of application labels to generate diagrams only for those specific applications.

  ```python
  GRAPH_MODELS = {
      'app_labels': ["core", "auth"],
  }
  ```

### `graph_models` Command-Line Options

The `graph_models` command also provides several command-line options to customize the output.

- **`-I <modelname1>,<modelname2>,...` or `--include-models <modelname1>,<modelname2>,...`**: To include only the specified models in the diagram.

  ```bash
  python manage.py graph_models core -I Restaurant,Sale > models.dot
  ```

- **`-X <modelname1>,<modelname2>,...` or `--exclude-models <modelname1>,<modelname2>,...`**: To exclude the specified models from the diagram.

  ```bash
  python manage.py graph_models core -X StaffRestaurant > models.dot
  ```

- **`--no-edges`**: To generate the diagram without the relationship lines (edges).

  ```bash
  python manage.py graph_models core --no-edges > models.dot
  ```

- **`--arrow-shape <shape>`**: To customize the shape of the arrows representing relationships.

- Various other options exist to customize the appearance, such as colors. Consult the `django-extensions` documentation for a full list.

### Exporting the ER Diagram

Once you have generated the visual ER diagram using a Graphviz tool, you can typically export it to various image formats like **SVG** or **PNG**. These images can then be easily included in your project documentation, README files, or other materials.

By using the `graph_models` command, developers can easily create visual representations of their Django models and their relationships, which is invaluable for understanding, documenting, and communicating the database structure.
