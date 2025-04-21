import unittest
import os
from unittest.mock import patch, MagicMock
from ..ocr_predictor import PaddleAPIOCRPredictor


class TestPaddleAPIOCRPredictor(unittest.TestCase):
    @patch.dict(os.environ, {"PADDLE_OCR_HOST": "http://mockserver.com"})
    def test_init(self):
        predictor = PaddleAPIOCRPredictor()
        expected_url = "http://mockserver.com/predict/ocr_system"
        self.assertEqual(predictor.api_url, expected_url)

    @patch("requests.Session.post")
    def test_predict_success(self, mock_post):
        predictor = PaddleAPIOCRPredictor()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": [{"text_region": [[0, 0], [1, 0], [1, 1], [0, 1]],
                                                        "text": "mocked_text", 
                                                        "confidence": 0.99}]}
        mock_post.return_value = mock_response

        result = predictor.predict("mock_image_data")
        self.assertEqual(len(result), 1)
        result_box = result[0]
        text_region = result_box.text_region

        self.assertEqual(text_region.p1, (0, 0))
        self.assertEqual(text_region.p2, (1, 0))
        self.assertEqual(text_region.p3, (1, 1))
        self.assertEqual(text_region.p4, (0, 1))
        self.assertEqual(result_box.text, "mocked_text")
        self.assertEqual(result_box.confidence, 0.99)

    @patch("requests.Session.post")
    @patch("logging.Logger.error")
    def test_predict_failure(self, mock_logger_error, mock_post):
        predictor = PaddleAPIOCRPredictor()

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"results": []}
        mock_post.return_value = mock_response

        result = predictor.predict("mock_image_data")
        mock_logger_error.assert_called_with("model prediction failed")
        self.assertEqual(result, [])
