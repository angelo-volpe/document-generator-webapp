import base64
from itertools import product

import cv2
import numpy as np
import numpy.typing as npt
import pandas as pd
from django.db.models import QuerySet
from shapely import Polygon

from .image_utils import denormalise_box_coordinates, get_box_coords
from .models import Box
from .ocr_predictor import OCRPredictor


class DocumentProcessor:
    def __init__(
        self,
        template: npt.NDArray[np.uint8],
        document: npt.NDArray[np.uint8],
        template_boxes: QuerySet[Box, Box],
        ocr_predictor: OCRPredictor,
    ) -> None:
        self.document = document
        self.template = template
        self.template_boxes = template_boxes
        self.ocr_predictor = ocr_predictor

    def __align_images(self) -> npt.NDArray[np.uint8]:
        image_gray = cv2.cvtColor(self.document, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(self.template, cv2.COLOR_BGR2GRAY)

        orb = cv2.SIFT_create(500)
        keypoints1, descriptors1 = orb.detectAndCompute(image_gray, None)
        keypoints2, descriptors2 = orb.detectAndCompute(template_gray, None)

        # Match features.
        matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_SL2)
        matches = matcher.match(descriptors1, descriptors2, None)

        # Sort matches by score
        matches = sorted(matches, key=lambda x: x.distance, reverse=False)

        # Remove not so good matches
        num_good_matches = int(len(matches) * 0.15)
        matches = matches[:num_good_matches]

        # Extract location of good matches
        points1 = np.zeros((len(matches), 2), dtype=np.float32)
        points2 = np.zeros((len(matches), 2), dtype=np.float32)

        for i, match in enumerate(matches):
            points1[i, :] = keypoints1[match.queryIdx].pt
            points2[i, :] = keypoints2[match.trainIdx].pt

        # Find homography
        h, _ = cv2.findHomography(points1, points2, cv2.RANSAC)

        # Use homography
        height, width = template_gray.shape

        return cv2.warpPerspective(self.document, h, (width, height))

    def __tag_boxes(self) -> None:
        doc_height, doc_width = self.template.shape[:2]

        template_boxes = [
            {
                "box_name": x.name,
                "box_id": x.pk,
                "coords": get_box_coords(
                    *denormalise_box_coordinates(
                        x.start_x_norm,
                        x.start_y_norm,
                        x.end_x_norm,
                        x.end_y_norm,
                        doc_width,
                        doc_height,
                    )
                ),
            }
            for x in self.template_boxes
        ]

        colliding_boxes = []
        for prediction, label_box in product(self.__predictions, template_boxes):
            pred_poly = Polygon(prediction.text_region)
            label_poly = Polygon(label_box["coords"])

            pred_area = pred_poly.area
            label_area = label_poly.area
            intersection_area = pred_poly.intersection(label_poly).area

            if intersection_area > 0:
                colliding_boxes.append(
                    {
                        "box_id": label_box["box_id"],
                        "box_name": label_box["box_name"],
                        "detected_box_text": prediction.text,
                        "detected_box_text_confidence": prediction.confidence,
                        "intersection_recall": intersection_area / label_area,
                        "intersection_precision": intersection_area / pred_area,
                        "coords_norm": [
                            [x[0] / doc_width, x[1] / doc_height] for x in prediction.text_region
                        ],
                    }
                )

        if colliding_boxes:
            self.detected_boxes_df = (
                pd.DataFrame(colliding_boxes)
                .sort_values(
                    by=["intersection_precision", "intersection_recall"],
                    ascending=False,
                )
                .drop_duplicates(subset="box_id")
            )
        else:
            self.detected_boxes_df = pd.DataFrame(
                columns=[
                    "box_id",
                    "box_name",
                    "detected_box_text",
                    "detected_box_text_confidence",
                    "intersection_recall",
                    "intersection_precision",
                    "coords_norm",
                ]
            )

    def process_document(self) -> None:
        registered_image = self.__align_images()
        _, buffer = cv2.imencode(".png", registered_image)
        self.encoded_image = base64.b64encode(buffer).decode("utf8")

        self.__predictions = self.ocr_predictor.predict(self.encoded_image)

        # TODO this part can be not necessary or different for some predictors returning classes
        self.__tag_boxes()
