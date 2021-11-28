import csv
import pandas as pd 
import uuid
from sqlalchemy import create_engine
import os


conn_url = 'postgres://airflow:airflow@postgres/airflow'

sqlalchemy_engine = create_engine(conn_url, 
                                    # echo = True
                                    )

# csv_path = '/data/detail_item_cleaned.csv'      #path inside container

query_create_batdongsan = ''' 
    CREATE TABLE items_final (
        district varchar,
        title varchar,
        price varchar,
        area varchar,
        phone varchar,
        bedroom varchar,
        toilet varchar,
        project_name varchar,
        project_id_link varchar,
        investor varchar,
        contact_name varchar,
        created_date varchar,
        expire_date varchar,
        posting_type varchar,
        posting_id varchar,
        price_in_mil_vnd int,
        area_in_m2 int,
        num_of_bedroom int,
        num_of_toilet int,
        created_date_c date, 
        expire_date_c date,
        apartment_vector varchar
        ); '''

def check_if_table_exists(engine=sqlalchemy_engine, table_name = 'items_final'):
    """Return boolean: True if the table exists, False otherwise """
    return engine.dialect.has_table(engine, table_name)

def upsert_table(district, engine=sqlalchemy_engine, table_name = 'items_final'):
    # https://stackoverflow.com/questions/61366664/how-to-upsert-pandas-dataframe-to-postgresql-table
    file_path='/data/detail_item_cleaned_{}.csv'.format(district)
    df = pd.read_csv(file_path, index_col='posting_id')

    temp_table_name = f"temp_{uuid.uuid4().hex[:6]}"        
    df.to_sql(temp_table_name, engine, index=True)          # tạo table trong postgres với tên temp_table_name
    
    index = list(df.index.names)                   
    index_sql_txt = ", ".join([f'"{i}"' for i in index])
    columns = list(df.columns)
    headers = index + columns
    headers_sql_txt = ", ".join([f'"{i}"' for i in headers])
    update_column_stmt = ", ".join([f'"{col}" = EXCLUDED."{col}"' for col in columns])


    # For the ON CONFLICT clause, postgres requires that the columns have unique constraint
    query_pk = f"""
    ALTER TABLE "{table_name}" DROP CONSTRAINT IF EXISTS unique_constraint_for_upsert;
    ALTER TABLE "{table_name}" ADD CONSTRAINT unique_constraint_for_upsert UNIQUE ({index_sql_txt});
    """
    engine.execute(query_pk)

    # Compose and execute upsert query
    query_upsert = f"""
        INSERT INTO "{table_name}" ({headers_sql_txt}) 
        SELECT {headers_sql_txt} FROM "{temp_table_name}"
        ON CONFLICT ({index_sql_txt}) DO UPDATE 
        SET {update_column_stmt};
        """
    engine.execute(query_upsert)

def insert_from_csv(district):
    file_path='/data/detail_item_cleaned_{}.csv'.format(district) 
    df = pd.read_csv(file_path, index_col='posting_id')
    df.to_sql('items_final', con=sqlalchemy_engine, if_exists='replace',index_label='posting_id')


my_district_list = ['quan-1','quan-2','quan-3','quan-4','quan-5','quan-6','quan-7','quan-8','quan-9','quan-10','quan-11','quan-12']
def merge_table(district_list=my_district_list):
    for district in district_list:
        if check_if_table_exists() is False:
            try:
                insert_from_csv(district)
                print('Successfully insert initial data from {}'.format(district))
            except FileNotFoundError:
                print('File not found error: {}'.format(district))
        else:
            try:
                upsert_table(district)
                print('Successfully upsert data from {}'.format(district))
            except FileNotFoundError:
                print('File not found error: {}'.format(district))