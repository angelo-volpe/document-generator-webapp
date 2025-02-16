from abc import ABC, abstractmethod
from enum import Enum
import os
import requests
from requests.auth import HTTPBasicAuth


class JobType(Enum):
    SAMPLE_GENERATION = 1
    MODEL_FINE_TUNING = 2


class Jobs(ABC):
    def run_job(self, job_type: JobType, job_args: dict):
        if job_type == JobType.SAMPLE_GENERATION:
            run_id = self._run_sampling_job(job_args)

        elif job_type == JobType.MODEL_FINE_TUNING:
            run_id = self._run_fine_tuning_job(job_args)

        return run_id

    @abstractmethod
    def _run_sampling_job(self, job_args: dict):
        pass

    @abstractmethod
    def _run_fine_tuning_job(self, job_args: dict):
        pass


class AirflowJobs(Jobs):
    def __init__(self):
        super().__init__()
        self.airflow_api_url = os.environ.get("AIRFLOW_API_URL")
        self.airflow_user = os.environ.get("AIRFLOW_USER")
        self.airflow_password = os.environ.get("AIRFLOW_PASSWORD")

    def __run_airflow_job(self, dag_id: str, conf: dict):
        url = f"{self.airflow_api_url}/{dag_id}/dagRuns"
        with requests.Session() as session:
            response = session.post(
                url,
                json=conf,
                auth=HTTPBasicAuth(self.airflow_user, self.airflow_password),
                timeout=10,
            )

        if response.status_code == 200:
            return response.json()["dag_run_id"]
        else:
            raise Exception(f"Failed to trigger job: {response.text}")

    def _run_sampling_job(self, job_args: dict):
        if "document_id" not in job_args or "num_samples" not in job_args:
            raise ValueError(
                "document_id and num_samples are required for sample generation job"
            )

        sampling_dag_id = os.environ.get("SAMPLING_DAG_ID", "generate_document_samples")
        conf = {
            "conf": {
                "document_id": job_args.get("document_id"),
                "num_samples": job_args.get("num_samples"),
            }
        }

        self.__run_airflow_job(sampling_dag_id, conf)

    def _run_fine_tuning_job(self, job_args: dict):
        if "document_id" not in job_args:
            raise ValueError("document_id is required for model fine tuning job")

        fine_tuning_dag_id = os.environ.get(
            "MODEL_FINE_TUNING_DAG_ID", "model_training"
        )
        conf = {
            "conf": {
                "document_id": job_args.get("document_id"),
            }
        }

        self.__run_airflow_job(fine_tuning_dag_id, conf)
