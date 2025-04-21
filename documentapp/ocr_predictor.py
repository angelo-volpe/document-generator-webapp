from abc import ABC, abstractmethod
import os
import requests
import json
from dataclasses import dataclass
from typing import List, Tuple

from .logging_config import logger


@dataclass
class TextRegion:
    p1: Tuple[int, int]
    p2: Tuple[int, int]
    p3: Tuple[int, int]
    p4: Tuple[int, int]

    def __iter__(self):
        return iter((self.p1, self.p2, self.p3, self.p4))

@dataclass
class PredictedBox:
    text_region: TextRegion
    text: str
    confidence: float


class OCRPredictor(ABC):
    @abstractmethod
    def predict(self, encoded_image) -> List[PredictedBox]:
        """
        Predicts the text boxes in the given image.
        :param encoded_image: The image to predict text boxes for, encoded in base64.
        :return: A list of predicted boxes, each containing the coordinates of the box and the predicted text.
        """
        pass


class PaddleAPIOCRPredictor(OCRPredictor):
    def __init__(self):
        self.api_url = f"{os.environ.get("PADDLE_OCR_HOST")}/predict/ocr_system"

    def predict(self, encoded_image) -> List[PredictedBox]:
        data = {"images": [encoded_image]}
        logger.debug(f"making request to {self.api_url}")
        with requests.Session() as session:
            response = session.post(
                self.api_url,
                headers={"Content-type": "application/json"},
                data=json.dumps(data),
            )

        if response.status_code != 200:
            logger.error("model prediction failed")

        res = response.json()["results"]

        predictions = []
        for prediction in res:
           predicted_box = PredictedBox(
               text_region=TextRegion(
                    p1=tuple(prediction["text_region"][0]),
                    p2=tuple(prediction["text_region"][1]),
                    p3=tuple(prediction["text_region"][2]),
                    p4=tuple(prediction["text_region"][3])
                ),
                text=prediction["text"],
                confidence=prediction["confidence"],
            )
           
           predictions.append(predicted_box)

        return predictions


class FCNNPaddleAPIOCRPredictor(OCRPredictor):
    def __init__(self):
        self.api_url = f"{os.environ.get("FCNN_PADDLE_OCR_HOST")}/predict"

    # TODO Can be refactored by implementing a common method for API call in like APIOCRPredictor class
    def predict(self, encoded_image) -> List[PredictedBox]:
        data = {"image": encoded_image}
        logger.debug(f"making request to {self.api_url}")
        with requests.Session() as session:
            response = session.post(
                self.api_url,
                headers={"Content-type": "application/json"},
                data=json.dumps(data),
            )

        if response.status_code != 200:
            logger.error("model prediction failed")

        res = response.json()["predictions"]

        predictions = []
        for prediction in res:
            x1, y1, x2, y2 = prediction["original_box"]
            predicted_box = PredictedBox(
                text_region=TextRegion(
                    p1=(x1, y1),
                    p2=(x2, y1),
                    p3=(x2, y2),
                    p4=(x1, y2)
                ),
                text=prediction["predicted_text"],
                confidence=prediction["text_score"],
            )
            predictions.append(predicted_box)

        return predictions