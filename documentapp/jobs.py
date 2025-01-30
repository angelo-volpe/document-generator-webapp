from abc import ABC, abstractmethod
from enum import Enum
import os
import requests
from requests.auth import HTTPBasicAuth


class JobType(Enum):
    SAMPLE_GENERATION = 1
    MODEL_TRAINING = 2


class Jobs(ABC):
    @abstractmethod
    def run_job(self, job_type: JobType):
        pass 


class AirflowJobs(Jobs):
    def __init__(self):
        super().__init__()
        self.airflow_api_url = os.environ.get("AIRFLOW_API_URL")
        self.airflow_user = os.environ.get("AIRFLOW_USER")
        self.airflow_password = os.environ.get("AIRFLOW_PASSWORD")
        
    
    def run_job(self, job_type: JobType, job_args: dict):
        if job_type == JobType.SAMPLE_GENERATION:
            if "document_id" not in job_args or "num_samples" not in job_args:
                raise ValueError("document_id and num_samples are required for sample generation job")

            sampling_dag_id = os.environ.get("SAMPLING_DAG_ID", "generate_document_samples")
            url = f"{self.airflow_api_url}/{sampling_dag_id}/dagRuns"
            conf = {
                "conf": {"document_id": job_args.get("document_id"),
                         "num_samples": job_args.get("num_samples")}
                }

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
                raise Exception(f"Failed to trigger sample generation job: {response.text}")

        elif job_type == JobType.MODEL_TRAINING:
            pass