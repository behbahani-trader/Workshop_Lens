Installation
============

There are two ways to install Lens Workshop: using Docker or installing directly.

Using Docker
-----------

1. Clone the repository:

.. code-block:: bash

   git clone https://github.com/yourusername/lens-workshop.git
   cd lens-workshop

2. Run with Docker Compose:

.. code-block:: bash

   docker-compose up --build

Direct Installation
-----------------

1. Clone the repository:

.. code-block:: bash

   git clone https://github.com/yourusername/lens-workshop.git
   cd lens-workshop

2. Create a virtual environment:

.. code-block:: bash

   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install Python dependencies:

.. code-block:: bash

   pip install -r requirements.txt

4. Install Node.js dependencies:

.. code-block:: bash

   npm install

5. Build static files:

.. code-block:: bash

   npm run build

6. Run the application:

.. code-block:: bash

   python app.py

Configuration
------------

The application can be configured using environment variables or a `.env` file. Here are the available options:

* ``FLASK_APP``: The Flask application to run (default: ``app.py``)
* ``FLASK_ENV``: The Flask environment (default: ``development``)
* ``SECRET_KEY``: The secret key for the application
* ``DATABASE_URL``: The database URL (default: ``sqlite:///app.db``)

Development Installation
----------------------

For development, you need to install additional dependencies:

.. code-block:: bash

   pip install -r requirements-dev.txt

This will install:

* Testing tools (pytest, pytest-cov, pytest-flask)
* Linting tools (flake8, black, isort)
* Type checking tools (mypy)
* Documentation tools (Sphinx) 