import unittest
from unittest.mock import MagicMock, patch
import numpy as np
import pandas as pd

from ..ocr_predictor import PredictedBox, TextRegion
from ..document_processor import DocumentProcessor


class TestDocumentProcessor(unittest.TestCase):
    def setUp(self):
        self.template = np.zeros((100, 100, 3), dtype=np.uint8)
        self.document = np.zeros((100, 100, 3), dtype=np.uint8)
        self.template_boxes = [
            {
                "name": "box1",
                "id": 1,
                "start_x_norm": 0.1,
                "start_y_norm": 0.1,
                "end_x_norm": 0.5,
                "end_y_norm": 0.5,
            }
        ]
        self.ocr_predictor = MagicMock()
        self.ocr_predictor.predict.return_value = [
            PredictedBox(
                text_region=TextRegion(
                    p1=(10, 10),
                    p2=(50, 10),
                    p3=(50, 50),
                    p4=(10, 50),
                ),
                text="sample text",
                confidence=0.95,
            )
        ]
        self.processor = DocumentProcessor(
            self.template, self.document, self.template_boxes, self.ocr_predictor
        )

    @patch("cv2.findHomography", return_value=(np.eye(3), None))
    @patch("cv2.warpPerspective", side_effect=lambda img, h, size: img)
    def test_align_images(self, mock_warp, mock_homography):
        registered_image = self.processor._DocumentProcessor__align_images()
        self.assertTrue(np.array_equal(registered_image, self.document))

    @patch("cv2.imencode", return_value=(True, np.array([1, 2, 3])))
    @patch("base64.b64encode", return_value=b"encoded_image")
    @patch.object(
        DocumentProcessor,
        "_DocumentProcessor__align_images",
        return_value=np.zeros((100, 100, 3), dtype=np.uint8),
    )
    def test_process_document(self, mock_b64encode, mock_imencode, mock_align_images):
        self.processor.process_document()
        mock_align_images.assert_called_once()
        self.ocr_predictor.predict.assert_called_once()
        self.assertEqual(self.processor.encoded_image, "encoded_image")
        self.assertIsInstance(self.processor.detected_boxes_df, pd.DataFrame)

    def test_tag_boxes(self):
        self.processor._DocumentProcessor__predictions = [
            PredictedBox(
                text_region=TextRegion(
                    p1=(10, 10),
                    p2=(50, 10),
                    p3=(50, 50),
                    p4=(10, 50),
                ),
                text="sample text",
                confidence=0.95,
            )
        ]
        self.processor._DocumentProcessor__tag_boxes()
        self.assertFalse(self.processor.detected_boxes_df.empty)
        self.assertIn("box_id", self.processor.detected_boxes_df.columns)
        self.assertIn("detected_box_text", self.processor.detected_boxes_df.columns)
