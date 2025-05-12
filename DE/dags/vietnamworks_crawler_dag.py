from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import ExternalPythonOperator
from datetime import datetime, timedelta
from clean import linkedin_indeed_clean, vietnamworks_clean
from crawl import vietnamworks_crawler, linkedin_indeed_crawler
from load import load_to_qdrant
from merge import merge_job
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

default_args = {
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(seconds=30),
}

with DAG('job_data_pipeline_bash',
         default_args=default_args,
         schedule_interval=None,
         catchup=False) as dag:

    venv_python = "/opt/venvs/venv/bin/python"

    crawl_linkedin = ExternalPythonOperator(
        task_id='crawl_linkedin_indeed',
        python=venv_python,
        python_callable=linkedin_indeed_crawler.main
    )

    crawl_vietnamworks = ExternalPythonOperator(
        task_id='crawl_vietnamworks',
        python=venv_python,
        python_callable=vietnamworks_crawler.crawl_vietnamworks_jobs
    )

    clean_linkedin = ExternalPythonOperator(
        task_id='clean_linkedin_indeed',
        python=venv_python,
        python_callable=linkedin_indeed_clean.main
    )

    clean_vietnamworks = ExternalPythonOperator(
        task_id='clean_vietnamworks',
        python=venv_python,
        python_callable=vietnamworks_clean.main
    )

    merge = ExternalPythonOperator(
        task_id='merge_jobs',
        python=venv_python,
        python_callable=merge_job.main
    )



    load_to_qdrant = ExternalPythonOperator(
        task_id='load_to_qdrant',
        python=venv_python,
        python_callable=load_to_qdrant.main
    )

    crawl_linkedin >> clean_linkedin
    crawl_vietnamworks >> clean_vietnamworks
    [clean_linkedin, clean_vietnamworks] >> merge
    merge >> load_to_qdrant
