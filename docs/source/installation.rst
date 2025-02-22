Installation and Run
====================
To install and run Document App, you need to have Docker and Docker Compose installed on your machine.

Then you can run it with the following commands:

.. code-block:: bash

   docker compose up

[Only firs time] Initialise the database:

.. code-block:: bash

    python manage.py makemigrations
    docker compose exec document_app python manage.py migrate --noinput