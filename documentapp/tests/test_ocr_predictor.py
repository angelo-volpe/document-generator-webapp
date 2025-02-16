import unittest
import os
from unittest.mock import patch, MagicMock
from ..ocr_predictor import PaddleAPIOCRPredictor


class TestPaddleAPIOCRPredictor(unittest.TestCase):
    @patch.dict(os.environ, {"PADDLE_OCR_HOST": "http://mockserver.com"})
    def test_init(self):
        predictor = PaddleAPIOCRPredictor(document_id=123)
        expected_url = "http://mockserver.com/predict/ocr_system_document_123"
        self.assertEqual(predictor.api_url, expected_url)

    @patch("requests.Session.post")
    def test_predict_success(self, mock_post):
        predictor = PaddleAPIOCRPredictor(document_id=123)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": ["mocked_text"]}
        mock_post.return_value = mock_response

        result = predictor.predict("mock_image_data")
        self.assertEqual(result, "mocked_text")

    @patch("requests.Session.post")
    @patch("logging.Logger.error")
    def test_predict_failure(self, mock_logger_error, mock_post):
        predictor = PaddleAPIOCRPredictor(document_id=123)

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"results": []}
        mock_post.return_value = mock_response

        result = predictor.predict("mock_image_data")
        mock_logger_error.assert_called_with("model prediction failed")
        self.assertEqual(result, [])
