import os
import unittest
from unittest.mock import patch

from requests.exceptions import RequestException

from ..jobs import AirflowJobs


class TestAirflowJobs(unittest.TestCase):
    @patch("requests.Session.post")
    @patch.dict(
        os.environ,
        {
            "AIRFLOW_API_URL": "http://mock-airflow.com",
            "AIRFLOW_USER": "user",
            "AIRFLOW_PASSWORD": "pass",
            "SAMPLING_DAG_ID": "sample_dag",
            "MODEL_FINE_TUNING_DAG_ID": "fine_tune_dag",
        },
    )
    def test_run_sampling_job_success(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"dag_run_id": "1234"}

        job = AirflowJobs()
        job_args = {"document_id": "doc123", "num_samples": 10}

        with patch.object(
            job, "_AirflowJobs__run_airflow_job", return_value="1234"
        ) as mock_airflow:
            job._run_sampling_job(job_args)
            mock_airflow.assert_called_once_with("sample_dag", {"conf": job_args})

    @patch("requests.Session.post")
    @patch.dict(
        os.environ,
        {
            "AIRFLOW_API_URL": "http://mock-airflow.com",
            "AIRFLOW_USER": "user",
            "AIRFLOW_PASSWORD": "pass",
            "MODEL_FINE_TUNING_DAG_ID": "fine_tune_dag",
        },
    )
    def test_run_fine_tuning_job_success(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"dag_run_id": "5678"}

        job = AirflowJobs()
        job_args = {"document_id": "doc456"}

        with patch.object(
            job, "_AirflowJobs__run_airflow_job", return_value="5678"
        ) as mock_airflow:
            job._run_fine_tuning_job(job_args)
            mock_airflow.assert_called_once_with("fine_tune_dag", {"conf": job_args})

    def test_run_sampling_job_missing_args(self):
        job = AirflowJobs()

        with self.assertRaises(ValueError):
            job._run_sampling_job({"document_id": "doc123"})

        with self.assertRaises(ValueError):
            job._run_sampling_job({"num_samples": 10})

    def test_run_fine_tuning_job_missing_args(self):
        job = AirflowJobs()

        with self.assertRaises(ValueError):
            job._run_fine_tuning_job({})

    @patch("requests.Session.post")
    @patch.dict(
        os.environ,
        {
            "AIRFLOW_API_URL": "http://mock-airflow.com",
            "AIRFLOW_USER": "user",
            "AIRFLOW_PASSWORD": "pass",
        },
    )
    def test_run_airflow_job_failure(self, mock_post):
        mock_post.return_value.status_code = 500
        mock_post.return_value.text = "Internal Server Error"

        job = AirflowJobs()

        with self.assertRaises(Exception) as context:
            job._AirflowJobs__run_airflow_job("some_dag", {"conf": {}})

        self.assertIn("Failed to trigger job", str(context.exception))

    @patch("requests.Session.post", side_effect=RequestException("Network Error"))
    def test_run_airflow_job_network_error(self, mock_post):
        job = AirflowJobs()

        with self.assertRaises(RequestException):
            job._AirflowJobs__run_airflow_job("some_dag", {"conf": {}})
