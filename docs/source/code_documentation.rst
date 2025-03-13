Code Documentation
==================

The code is divided into the following modules
This repo uses Hexagonal Architecture to separate the concerns of the application and make the external modules(jobs providers, ocr providers) interchangeable.

Views
-----
Path: documentapp/views.py
Contains the views for the frontend.

API
---
Path: documentapp/api.py

Contains:
- REST API for Document Template, Document Sample and Boxes.
- Job API for Document Sample Generation and Model Training.

OCRPredictor
-------------
Path: documentapp/ocr_predictor.py

Interface for OCR Predictor.
Implement the predict method to predict the content of a document image.

Currently implemented with PaddleOCR.

Jobs
----
Path: documentapp/jobs.py

Interface for Jobs.
Implement the run_job method to run the job.

Currently implemented with Airflow.