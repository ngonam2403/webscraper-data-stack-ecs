# -*- coding: UTF-8 -*- 

import pandas as pd
import re
from datetime import datetime
import os 
import numpy as np 
# import farmhash
from utils import timer

def convert_all_to_string(my_text):
    my_text = str(my_text)
    return my_text

def remove_redundant_char(my_text):
    my_text = my_text.strip("[' ']")
    my_text = my_text.replace("\\n","")
    my_text = my_text.replace('"', '')
    my_text = my_text.strip()
    my_text = my_text.replace("[]","")   
    return my_text

def find_number(my_text):
    # https://stackoverflow.com/questions/4289331/how-to-extract-numbers-from-a-string-in-python
    my_text = re.findall(r'\d+', my_text)
    try:
        my_text = my_text[0]
    except:
        my_text = 0
    return my_text

def convert_to_date(my_text): 
    # https://towardsdatascience.com/10-quick-python-snippets-that-can-help-you-work-with-dates-831f4f27aa05
    my_date = datetime.strptime(my_text, '%d/%m/%Y').date()
    return my_date

# my_source_file_path = '/home/ec2-user/efs/try-default-airflow-docker-ecs/data/item_quan-8.csv'
# my_dest_file_path = '/home/ec2-user/efs/try-default-airflow-docker-ecs/data/detail_item_cleaned.csv'

def one_clean_button(district): 
    file_path='/data/item_{}.csv'.format(district)      # path inside container
    df = pd.read_csv(file_path) 
    df = df.drop_duplicates()

    # convert all to string before cleaning
    df = df.applymap(lambda x: convert_all_to_string(x))

    # remove character
    df = df.applymap(lambda x: remove_redundant_char(x))

    # convert string to number for later processing
    df['price_in_mil_vnd'] = df['price'].apply(lambda x: find_number(x))
    df['area_in_m2'] = df['area'].apply(lambda x: find_number(x))
    df['num_of_bedroom'] = df['bedroom'].apply(lambda x: find_number(x))
    df['num_of_toilet'] = df['toilet'].apply(lambda x: find_number(x))

    # convert string to date for later processing
    df['created_date_c'] = df['created_date'].apply(lambda x: convert_to_date(x))
    df['expire_date_c'] = df['expire_date'].apply(lambda x: convert_to_date(x))

    # make a fingerprint for each apartment: 
    df['apartment_vector'] = df[['area_in_m2','num_of_bedroom','project_name','investor']].values.tolist()

    ## https://www.geeksforgeeks.org/python-program-to-convert-a-list-to-string/
    # df['apartment_fingerprint'] =  df['apartment_vector'].apply(lambda x: np.uint64(farmhash.fingerprint64('-'.join(x))).astype('int64'))
    
    df.set_index('posting_id')

    # save to csv
    df.to_csv('/data/detail_item_cleaned_{}.csv'.format(district), index=False) 
    print('successfully clean data of {} & land in stage area!'.format(district))

my_district_list = ['quan-1','quan-2','quan-3','quan-4','quan-5','quan-6','quan-7','quan-8','quan-9','quan-10','quan-11','quan-12']
def clean_all_district(district_list=my_district_list):
    for district in district_list:
        print(os.getcwd())
        try:
            one_clean_button(district)
        except FileNotFoundError:
            print('File not found error: {}'.format(district))



# one_clean_button(df=df)