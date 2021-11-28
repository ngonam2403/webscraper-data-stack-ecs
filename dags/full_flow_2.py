from datetime import datetime, timedelta 
import json 
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from sample_clean_raw_csv import clean_all_district
from sample_move_csv_to_postgres import merge_table

''''''''''''''''' START '''''''''''''''''''''
# DAG definition
default_args = {
    "owner": "airflow",
    # "depends_on_past": True,
    # "wait_for_downstream": True,
    "start_date": datetime(2021, 11, 10),
    "email": ["airflow@airflow.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

dag = DAG(
    "dag_clean_to_postgresql",
    default_args=default_args,
    schedule_interval="0 0 * * *",
    max_active_runs=1,
)

end_of_data_pipeline = DummyOperator(task_id="end_of_data_pipeline", dag=dag)

clean_raw_csv = PythonOperator(
    dag=dag,
    task_id='clean_raw_csv',
    python_callable=clean_all_district
)

move_csv_to_postgres = PythonOperator(
    dag=dag,
    task_id='move_csv_to_postgres',
    python_callable=merge_table
)


clean_raw_csv >> move_csv_to_postgres >> end_of_data_pipeline
