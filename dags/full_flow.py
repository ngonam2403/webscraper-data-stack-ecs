from datetime import datetime, timedelta 
import json 
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from sample_crawl_to_csv import crawl_to_csv

''''''''''''''''' START '''''''''''''''''''''
# DAG definition
default_args = {
    "owner": "airflow",
    "start_date": datetime(2021, 11, 10),
    "email": ["airflow@airflow.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

dag = DAG(
    "dag_crawl_to_csv",
    default_args=default_args,
    schedule_interval="0 0 * * *",      # once a day
    max_active_runs=1,
)

end_of_data_pipeline = DummyOperator(task_id="end_of_data_pipeline", dag=dag)

crawl_to_csv = PythonOperator(
    dag=dag,
    task_id='crawl_to_csv',
    python_callable=crawl_to_csv
)


crawl_to_csv >> end_of_data_pipeline