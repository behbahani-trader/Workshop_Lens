Development
===========

This section provides information for developers who want to contribute to the project.

Setup Development Environment
---------------------------

1. Clone the repository:

   .. code-block:: bash

       git clone https://github.com/yourusername/lens-workshop.git
       cd lens-workshop

2. Create and activate a virtual environment:

   .. code-block:: bash

       python -m venv venv
       source venv/bin/activate  # Linux/Mac
       venv\Scripts\activate     # Windows

3. Install development dependencies:

   .. code-block:: bash

       pip install -r requirements-dev.txt

4. Set up pre-commit hooks:

   .. code-block:: bash

       pre-commit install

5. Create a `.env` file with development settings:

   .. code-block:: text

       FLASK_APP=app
       FLASK_ENV=development
       FLASK_DEBUG=1
       SECRET_KEY=your-secret-key
       DATABASE_URL=sqlite:///dev.db

6. Initialize the database:

   .. code-block:: bash

       flask db upgrade

7. Run the development server:

   .. code-block:: bash

       flask run

Code Style
---------

The project follows PEP 8 style guide. Use the following tools to maintain code quality:

* flake8 for linting
* black for code formatting
* isort for import sorting
* mypy for type checking

Run the following command to check code style:

.. code-block:: bash

    make lint

Testing
-------

The project uses pytest for testing. Run tests with:

.. code-block:: bash

    make test

To run tests with coverage:

.. code-block:: bash

    make test-cov

Documentation
------------

The project uses Sphinx for documentation. Build the documentation with:

.. code-block:: bash

    make docs

View the documentation by opening `docs/_build/html/index.html` in your browser.

Project Structure
---------------

::

    lens-workshop/
    ├── app/
    │   ├── __init__.py
    │   ├── models/
    │   ├── routes/
    │   ├── static/
    │   └── templates/
    ├── docs/
    ├── tests/
    ├── .env
    ├── .gitignore
    ├── config.py
    ├── requirements.txt
    └── requirements-dev.txt

Database Migrations
-----------------

The project uses Flask-Migrate for database migrations. To create a new migration:

.. code-block:: bash

    flask db migrate -m "Description of changes"

To apply migrations:

.. code-block:: bash

    flask db upgrade

To rollback migrations:

.. code-block:: bash

    flask db downgrade

Docker Development
----------------

For Docker development:

1. Build the development image:

   .. code-block:: bash

       docker-compose -f docker-compose.dev.yml build

2. Start the development containers:

   .. code-block:: bash

       docker-compose -f docker-compose.dev.yml up

3. Run tests in Docker:

   .. code-block:: bash

       docker-compose -f docker-compose.dev.yml run web make test

4. Run linting in Docker:

   .. code-block:: bash

       docker-compose -f docker-compose.dev.yml run web make lint 