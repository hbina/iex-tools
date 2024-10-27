from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta


start_date = datetime(2023, 10, 5)
end_date = datetime(2023, 10, 15)


with DAG(
    dag_id="process_iex_pcap2",
    default_args={
        "retries": 0,
        "retry_delay": timedelta(minutes=5),
    },
    start_date=start_date,
    end_date=end_date,
    schedule_interval="0 0 * * *",
    catchup=True,
) as dag:
    date_str = "{{ ds }}".replace("-", "")
    print(f"date_str:{date_str}")
    # zcat 20240226_DEEP1.0.pcap.gz | zstd --compress -20 --ultra -o 20240226_DEEP1.0.pcap.zstd --force
    recompress_deep_pcap = BashOperator(
        task_id="recompress_deep_pcap2",
        bash_command=f"echo HELLO WORLD???",
    )

    recompress_deep_pcap
