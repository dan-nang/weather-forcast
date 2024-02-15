from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.utils.email import send_email
import requests
import psycopg2

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 2, 13),
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

def connection():
    conn = psycopg2.connect(host="host.docker.internal",
                            database="postgres",
                            user="postgres",
                            password="123")
    return conn

def fetch_weather_date():
    cur = connection().cursor()
    cur.execute("SELECT DATE FROM WEATHER_FORECAST ORDER BY DATE DESC LIMIT 1")
    last_date = cur.fetchall()
    current_date = datetime.now().date()
    end_date = current_date + timedelta(days=1)
    try:
        last_date = last_date[0][0]  # Extract the date from the first tuple in the list
        last_date = last_date.date()

        while last_date <= current_date:
            last_date += timedelta(days=1)
            fetch_and_store_weather_forecast(last_date)
    except:
        fetch_and_store_weather_forecast(current_date)
        fetch_and_store_weather_forecast(end_date)

def fetch_and_store_weather_forecast(cur_date):
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
    # call connection
    conn = psycopg2.connect(host="host.docker.internal",
                        database="postgres",
                        user="postgres",
                        password="123")
    cur = conn.cursor() 

    for forecast in hourly_forecast:
        if datetime.fromtimestamp(forecast["dt"]).date() == cur_date:
            forecast_time = datetime.fromtimestamp(forecast["dt"]).strftime("%Y-%m-%d %H:%M:%S")
            wind = forecast["wind"]["speed"]
            temperature = forecast["main"]["temp"]
            humidity = forecast["main"]["humidity"]
            description = forecast["weather"][0]["description"]
            insert_dt = datetime.now().date()
            # cur.execute("INSERT INTO weather_forecast (date, wind, temperature, humidity, forecast, insert_dt) VALUES (%s, %s, %s, %s, %s, %s)",
            #             (forecast_time, wind, temperature, humidity, description, insert_dt))
            cur.execute("""
                            MERGE INTO weather_forecast AS target
                            USING (VALUES (%s, %s, %s, %s, %s, %s)) AS source (date, wind, temperature, humidity, forecast, insert_dt)
                            ON target.date = CAST(%s AS TIMESTAMP)
                            WHEN MATCHED THEN
                                UPDATE SET wind = source.wind, temperature = source.temperature, humidity = source.humidity, forecast = source.forecast, insert_dt = source.insert_dt
                            WHEN NOT MATCHED THEN
                                INSERT (date, wind, temperature, humidity, forecast, insert_dt)
                                VALUES (CAST(%s AS TIMESTAMP), source.wind, source.temperature, source.humidity, source.forecast, source.insert_dt)
                        """,
                        (forecast_time, wind, temperature, humidity, description, insert_dt, forecast_time, forecast_time))

    conn.commit()
    cur.close()
    conn.close()
    
fetch_weather_task = PythonOperator(
    task_id='fetch_weather',
    python_callable=fetch_weather_date,
    dag=dag,
)

dag