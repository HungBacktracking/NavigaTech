from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

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

    # Clean
    clean_linkedin = BashOperator(
        task_id='clean_linkedin_indeed',
        bash_command='python3 /opt/airflow/dags/clean/linkedin_indeed_clean.py'
    )

    clean_vietnamworks = BashOperator(
        task_id='clean_vietnamworks',
        bash_command='python3 /opt/airflow/dags/clean/vietnamwork_clean.py'
    )

    # Merge
    merge = BashOperator(
        task_id='merge_jobs',
        bash_command='python3 /opt/airflow/dags/merge/merge_job.py'
    )
    
    crawl_linkedin >> clean_linkedin
    crawl_vietnamworks >> clean_vietnamworks
    [clean_linkedin, clean_vietnamworks] >> merge
