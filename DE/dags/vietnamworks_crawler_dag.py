from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
from clean import linkedin_indeed_clean
import os
import sys
from airflow.operators.python import PythonOperator


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

default_args = {
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(seconds=30),  # giảm delay giữa các lần retry
}

with DAG('job_data_pipeline_bash',
         default_args=default_args,
         schedule_interval=None,
         catchup=False) as dag:

    # Crawl
    crawl_linkedin = BashOperator(
        task_id='crawl_linkedin_indeed',
        bash_command='python3 /opt/airflow/dags/crawl/crawl_linkedin_indeed.py'
    )

    crawl_vietnamworks = BashOperator(
        task_id='crawl_vietnamworks',
        bash_command='python3 /opt/airflow/dags/crawl/vietnamworks_crawler.py'
    )

    clean_linkedin = PythonOperator(
        task_id='clean_linkedin_indeed',
        python_callable=linkedin_indeed_clean.main
    )

    clean_vietnamworks = BashOperator(
        task_id='clean_vietnamworks',
        bash_command='python3 /opt/airflow/dags/clean/vietnamwork_clean.py'
    )


    

    # Merge
    merge = BashOperator(
        task_id='merge_jobs',
        bash_command='''
        python3 /opt/airflow/dags/merge/merge_job.py
        '''
    )

    # Load to Qdrant
    load_to_qdrant = BashOperator(
        task_id='load_to_qdrant',
        bash_command='python3 -m venv /tmp/merge_venv && \
        source /tmp/merge_venv/bin/activate && \
        pip install sqlalchemy==2.0 && \
        pip install -r /opt/airflow/requirements.txt && \
        pip install qdrant-client && \
        pip install googletrans && \
        pip install "llama-index-embeddings-huggingface" && \
        pip install "qdrant-client[fastembed]" fastembed-gpu && \
        pip install "llama-index-embeddings-huggingface-api" && \
        python3 /opt/airflow/dags/load/load_to_qdrant/load_to_qdrant.py'
    )
    crawl_linkedin >> clean_linkedin
    crawl_vietnamworks >> clean_vietnamworks
    [clean_linkedin, clean_vietnamworks] >> merge
    merge >> load_to_qdrant
