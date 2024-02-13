from datetime import datetime, timedelta
# import os
# os.environ['AIRFLOW_HOME'] = '/airflow_config'
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.utils.email import send_email
import requests
import psycopg2
import pandas as pd


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 2, 12),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    dag_id='weather_forecast_dag',
    default_args=default_args,
    description='A DAG to fetch weather forecast and store in PostgreSQL',
    schedule_interval='0 0 * * *', # Cron expression for midnight every day
)

def fetch_and_store_weather_forecast():
    endpoint = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": 'Jakarta',
        "appid": '04e28a3f5f628d0895a3523b43a5a634',
        "units": "metric"
    }
    response = requests.get(endpoint, params=params)
    response.raise_for_status()  # Raise an exception if the request fails
    data = response.json()
    
    hourly_forecast = data['list']

    # Transform data and store in PostgreSQL
    conn = psycopg2.connect(host="host.docker.internal",
                            database="postgres",
                            user="postgres",
                            password="123")
    cur = conn.cursor()
    for forecast in hourly_forecast:
        if datetime.fromtimestamp(forecast["dt"]).date() == datetime.now().date():
            forecast_time = datetime.fromtimestamp(forecast["dt"]).strftime("%Y-%m-%d %H:%M:%S")
            wind = forecast["wind"]["speed"]
            temperature = forecast["main"]["temp"]
            humidity = forecast["main"]["humidity"]
            description = forecast["weather"][0]["description"]
            insert_dt = datetime.now().date()
            cur.execute("INSERT INTO weather_forecast (date, wind, temperature, humidity, forecast, insert_dt) VALUES (%s, %s, %s, %s, %s, %s)",
                        (forecast_time, wind, temperature, humidity, description, insert_dt))
    conn.commit()
    # cur.execute("SELECT date, wind, temperature, humidity, forecast,  FROM weather_forecast")
    # weather_data = cur.fetchall()
    cur.close()
    conn.close()
    # return weather_data

# def format_report(weather_data):
#     # Jinja templating to format the report dynamically
#     template = """
#     Weather Forecast Report:
#     {% for data in weather_data %}
#     Date: {{ data[0] }}, Wind: {{ data[1] }}, Temperature: {{ data[2] }}, Humidity: {{ data[3] }}, Forecast: {{ data[4] }}
#     {% endfor %}
#     """
#     formatted_report = template.render(weather_data=weather_data)
#     return formatted_report

# def send_email_report(formatted_report):
#     subject = "Weather Forecast Report"
#     recipients = ["danangwahyu0607@gmail.com"]
#     send_email(recipients, subject, formatted_report)

fetch_weather_task = PythonOperator(
    task_id='fetch_weather',
    python_callable=fetch_and_store_weather_forecast,
    dag=dag,
)
# format_report_task = PythonOperator(
#     task_id='format_report',
#     python_callable=format_report,
#     provide_context=True,
#     dag=dag,
# )

# send_email_task = PythonOperator(
#     task_id='send_email_report',
#     python_callable=send_email_report,
#     provide_context=True,
#     dag=dag,
# )

# fetch_weather_task >> format_report_task >> send_email_task

dag