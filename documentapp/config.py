import os
from .ocr_predictor import PaddleAPIOCRPredictor, FCNNPaddleAPIOCRPredictor


def get_ocr_predictor():
    """
    Returns the OCR predictor based on the environment variable.
    """
    if os.environ.get("OCR") == "PADDLE_OCR":
        return PaddleAPIOCRPredictor()
    elif os.environ.get("OCR") == "FCNN_PADDLE_OCR":
        return FCNNPaddleAPIOCRPredictor()
    else:
        raise ValueError("Invalid OCR predictor specified in environment variables")
