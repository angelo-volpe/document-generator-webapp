Installation and Run
====================
To install and run Document App, you need to have Docker and Docker Compose installed on your machine.

Frontend
--------
To deploy the forntend can run it the following commands inside the project:

.. code-block:: bash

   docker compose up

[Only first time] Initialise the database:

.. code-block:: bash

    python manage.py makemigrations
    docker compose exec document_app python manage.py migrate --noinput

Remember that to access all the functionalities you also need to run the job services and model services.

Job Services
------------

To deploy the job services, you need to clone the `document-generator-jobs <https://github.com/angelo-volpe/document-generator-jobs>`_ 
repository and run the following commands inside:

.. code-block:: bash
    # Build the docker image for jobs
    docker build . -t document-generator-jobs:latest

    # Start Airflow service
    cd airflow
    docker compose up airflow-init
    docker compose up

Model Services
--------------
To deploy the model services, you need to clone the `PaddleOCR <https://github.com/angelo-volpe/PaddleOCR>`_
repository.

Then you can build the docker image needed for training with the following command:
.. code-block:: bash
    docker build -f ./document_app_docker/Dockerfile_training -t paddle-ocr-document:latest .

And once a new model is ready you deploy it using the following command:
