from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from airflow.utils.trigger_rule import TriggerRule
import logging
import os

start_date = datetime(2023, 2, 22)
end_date = datetime(2023, 4, 25)
# end_date = datetime(2024, 3, 1)


def check_file_exists_func(file_path: str) -> str:
    if os.path.exists(file_path):
        return "recompress_top_pcap"
    return "skip_dag"


with DAG(
    dag_id="process_iex_pcap",
    default_args={
        "retries": 0,
        "retry_delay": timedelta(minutes=5),
    },
    start_date=start_date,
    end_date=end_date,
    schedule_interval="0 0 * * *",
    max_active_runs=1,
    catchup=True,
    fail_stop=True,
) as dag:
    # date_str = "{{ ds_nodash }}".replace("-", "")
    # assert "-" not in date_str
    # pcap_gz = "/usr/share/zfs_pool/iex/pcap/{{ ds_nodash }}_TOPS1.6.pcap.gz"
    # pcap_zst = "/usr/share/zfs_pool/iex/pcap/{{ ds_nodash }}_TOPS1.6.pcap.zst"
    # raw_folder = "/usr/share/zfs_pool/iex/raw/{{ ds_nodash }}/"
    # h5_file = "/usr/share/zfs_pool/iex/h5/{{ ds_nodash }}.h5"
    # gen_h5_script = "/usr/share/zfs_pool/git/iex-tools/scripts/randoms/gen_h5.py"

    check_file_exists = PythonOperator(
        task_id="check_file_exists",
        python_callable=check_file_exists_func,
        op_args=["/usr/share/zfs_pool/iex/pcap/{{ ds_nodash }}_TOPS1.6.pcap.gz"],
    )

    skip_dag = BashOperator(
        task_id="skip_dag",
        bash_command="echo 'File does not exist, so skipping. The file: /usr/share/zfs_pool/iex/pcap/{{ ds_nodash }}_TOPS1.6.pcap.gz'"
    )

    recompress_top_pcap = BashOperator(
        task_id="recompress_top_pcap",
        bash_command=(
            "zcat /usr/share/zfs_pool/iex/pcap/{{ ds_nodash }}_TOPS1.6.pcap.gz | "
            "zstd --compress -20 --ultra -o /usr/share/zfs_pool/iex/pcap/{{ ds_nodash }}_TOPS1.6.pcap.zst --force"
        ),
        skip_on_exit_code=None,
    )
    # delete_top_gz = BashOperator(
    #     task_id="delete_top_gz",
    #     bash_command="rm /usr/share/zfs_pool/iex/pcap/{{ ds_nodash }}_TOPS1.6.pcap.gz",
    # skip_on_exit_code=None,
    # )
    convert_pcap_to_raw = BashOperator(
        task_id="convert_pcap_to_raw",
        bash_command=(
            "ulimit -n 65536 && convert-pcap "
            "--input-path /usr/share/zfs_pool/iex/pcap/{{ ds_nodash }}_TOPS1.6.pcap.zst "
            "--output-path /usr/share/zfs_pool/iex/raw/{{ ds_nodash }}/"
        ),
        skip_on_exit_code=None,
    )
    convert_raw_to_h5 = BashOperator(
        task_id="convert_raw_to_h5",
        bash_command=(
            "python /usr/share/zfs_pool/git/iex-tools/scripts/randoms/gen_h5.py "
            "-i /usr/share/zfs_pool/iex/raw/{{ ds_nodash }}/ "
            "-o /usr/share/zfs_pool/iex/h5/{{ ds_nodash }}.h5"
        ),
        skip_on_exit_code=None,
    )
    delete_raw_folder = BashOperator(
        task_id="delete_top_gz",
        bash_command="rm -rf /usr/share/zfs_pool/iex/raw/{{ ds_nodash }}",
        skip_on_exit_code=None,
    )

    check_file_exists >> [skip_dag, recompress_top_pcap]
    recompress_top_pcap >> convert_pcap_to_raw >> convert_raw_to_h5 >> delete_raw_folder
