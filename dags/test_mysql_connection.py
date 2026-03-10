from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator


def test_via_provider():
    """Prueba la conexión usando el hook de MySQL de Airflow (apache-airflow-providers-mysql)."""
    from airflow.providers.mysql.hooks.mysql import MySqlHook

    hook = MySqlHook(mysql_conn_id="mysql_default")
    conn = hook.get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT VERSION()")
    version = cursor.fetchone()
    cursor.close()
    conn.close()
    print(f"[provider] MySQL version: {version[0]}")


def test_via_connector():
    """Prueba la conexión directa con mysql-connector-python usando las env vars."""
    import os
    import mysql.connector

    host = os.getenv("MYSQL_HOST", "mysql")
    port = int(os.getenv("MYSQL_PORT", 3306))
    user = os.getenv("MYSQL_USER", "user")
    password = os.getenv("MYSQL_PASSWORD", "user1234")
    database = os.getenv("MYSQL_DATABASE", "mydatabase")

    conn = mysql.connector.connect(
        host=host, port=port, user=user, password=password, database=database
    )
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    cursor.close()
    conn.close()
    print(f"[connector] Conectado a '{database}'. Tablas: {[t[0] for t in tables]}")


with DAG(
    dag_id="test_mysql_connection",
    description="Prueba de conectividad a MySQL desde Airflow",
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,  # solo manual
    catchup=False,
    tags=["test", "mysql"],
) as dag:

    task_provider = PythonOperator(
        task_id="test_via_airflow_provider",
        python_callable=test_via_provider,
    )

    task_connector = PythonOperator(
        task_id="test_via_mysql_connector",
        python_callable=test_via_connector,
    )

    task_provider >> task_connector
