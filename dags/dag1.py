
from datetime import timedelta
import requests
import great_expectations as ge
import pandas as pd
from datetime import datetime
import os


from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2020, 12, 20),
    #'email': ['dylanray93@gmail.com'],
    #'email_on_failure': True,
    #'email_on_retry': True,
    #'retries': 1,
    #'retry_delay': timedelta(minutes=1),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
    # 'wait_for_downstream': False,
    # 'dag': dag,
    # 'sla': timedelta(hours=2),
    # 'execution_timeout': timedelta(seconds=300),
    # 'on_failure_callback': some_function,
    # 'on_success_callback': some_other_function,
    # 'on_retry_callback': another_function,
    # 'sla_miss_callback': yet_another_function,
    # 'trigger_rule': 'all_success'
}

dag = DAG(
    dag_id='test1',
    default_args=default_args,
    description='Test DAG',
    schedule_interval='0 0 * * *',
)

def api_pull():

    response = requests.get("https://www.healthcare.gov/api/glossary.json")

    json_data = response.json()

    df = pd.DataFrame.from_dict(json_data["glossary"], orient='columns')

    file_name = str(datetime.now().date()) + '.csv'
    full_name = '/data/' + file_name

    with open(full_name,'w') as outputfile:
        df.to_csv(outputfile)

t1 = PythonOperator(
    task_id='pull_data',
    python_callable=api_pull,
    dag=dag
)

def test_expectations():
    test = ge.read_csv('/data/' + str(datetime.now().date()) + '.csv')
    validation_results = test.validate(expectation_suite = '/data/my_expectations.json')

    if validation_results["success"]:
        messagesuccess = "Success"
        return messagesuccess
    else:
        raise ValueError("Houston: we have a problem")

t2 = PythonOperator(
    task_id='check_expectations',
    python_callable=test_expectations,
    dag=dag
)

def keyword_exist():
    my_df = pd.read_csv('/data/' + str(datetime.now().date()) + '.csv')

    is_en = my_df['lang'] == 'en'

    my_df = my_df[is_en]

    if my_df['title'].str.contains('holistic').any():
        raise ValueError("The keyword was found in the article")
    else:
        not_contains = "The keyword was not found in an article title"
        return not_contains

t3 = PythonOperator(
    task_id='check_keyword',
    python_callable=keyword_exist,
    dag=dag
)

t1 >> t2 >> t3
