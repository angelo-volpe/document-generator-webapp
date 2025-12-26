import os

from .jobs import AirflowJobs, Jobs
from .ocr_predictor import FCNNPaddleAPIOCRPredictor, OCRPredictor, PaddleAPIOCRPredictor


def get_ocr_predictor() -> OCRPredictor:
    """
    Returns the OCR predictor based on the environment variable.
    """
    if os.environ.get("OCR") == "PADDLE_OCR":
        return PaddleAPIOCRPredictor()
    if os.environ.get("OCR") == "FCNN_PADDLE_OCR":
        return FCNNPaddleAPIOCRPredictor()
    raise ValueError("Invalid OCR predictor specified in environment variables")


def get_job_executor() -> Jobs:
    """
    Returns the Job executor based on the environment variable.
    """
    if os.environ.get("JOB_EXECUTOR") == "AIRFLOW":
        return AirflowJobs()
    raise ValueError("Invalid Job executor specified in environment variables")
