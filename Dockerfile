FROM apache/airflow:2.2.1
RUN pip install --no-cache-dir lxml 
RUN pip install --no-cache-dir selenium