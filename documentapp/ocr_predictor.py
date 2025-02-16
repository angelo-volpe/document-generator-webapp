from abc import ABC, abstractmethod
import os
import requests
import json
from .logging_config import logger


class OCRPredictor(ABC):
    @abstractmethod
    def predict(self, image) -> str:
        pass


class PaddleAPIOCRPredictor(OCRPredictor):
    def __init__(self, document_id: int):
        self.api_url = f"{os.environ.get("PADDLE_OCR_HOST")}/predict/ocr_system_document_{document_id}"

    def predict(self, image) -> str:
        data = {"images": [image]}
        with requests.Session() as session:
            response = session.post(
                self.api_url,
                headers={"Content-type": "application/json"},
                data=json.dumps(data),
            )

        if response.status_code != 200:
            logger.error("model prediction failed")

        predictions = response.json()["results"]

        return predictions[0] if len(predictions) > 0 else []
