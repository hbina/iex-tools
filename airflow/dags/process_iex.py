import logging
import os

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from airflow.utils.trigger_rule import TriggerRule
from airflow.decorators import dag, task

start_date = datetime(2022, 1, 1)
end_date = datetime(2024, 1, 1)
# end_date = datetime(2024, 3, 1)


# def check_file_exists_func(file_path: str) -> str:
#     if os.path.exists(file_path):
#         return "recompress_top_pcap"
#     return "skip_dag"


@task.bash
def download_tops_pcap() -> str:
    return (
        "python /home/hbina085/git/iex-tools/airflow/scripts/download_pcap.py "
        "-i /home/hbina085/git/iex-tools/scripts/randoms/links.csv "
        "-o /home/hbina085/tank/iex/pcap/ "
        "-d {{ ds_nodash }} "
        "-t TOPS"
    )


@task.bash
def decompress_tops_pcap() -> str:
    return "gunzip /tank/iex/pcap/{{ ds_nodash }}_IEXTP1_TOPS1.6.pcap.gz"


@task.bash
def recompress_top_pcap() -> str:
    return (
        "zstd --compress -20 --ultra --force "
        "-o /tank/iex/pcap/{{ ds_nodash }}_IEXTP1_TOPS1.6.pcap.zst "
        "/tank/iex/pcap/{{ ds_nodash }}_IEXTP1_TOPS1.6.pcap"
    )


@task.bash
def delete_original_source() -> str:
    return "rm /tank/iex/pcap/{{ ds_nodash }}_IEXTP1_TOPS1.6.pcap"


@task.bash
def convert_pcap_to_raw() -> str:
    return (
        "ulimit -n 65536 && convert-pcap "
        "--input-path /tank/iex/pcap/{{ ds_nodash }}_IEXTP1_TOPS1.6.pcap.zst "
        "--output-path /tank/iex/raw/{{ ds_nodash }}/"
    )


@task.bash
def convert_raw_to_h5() -> str:
    return (
        "python /tank/git/iex-tools/scripts/randoms/gen_h5.py "
        "-i /tank/iex/raw/{{ ds_nodash }}/ "
        "-o /tank/iex/h5/{{ ds_nodash }}.h5"
    )


@task.bash
def delete_raw_folder() -> str:
    return "rm -rf /tank/iex/raw/{{ ds_nodash }}"


with DAG(
    dag_id="process_iex_pcap",
    default_args={
        "retries": 0,
        "retry_delay": timedelta(minutes=5),
    },
    start_date=start_date,
    end_date=end_date,
    schedule_interval="0 0 * * *",
    max_active_runs=2,
    catchup=True,
    fail_stop=True,
):
    # download_tops_pcap = BashOperator(
    #     task_id="download_tops_pcap",
    #     bash_command=(
    #         "python /home/hbina085/git/iex-tools/airflow/scripts/download_pcap.py "
    #         "-i /home/hbina085/git/iex-tools/scripts/randoms/links.csv "
    #         "-o /home/hbina085/tank/iex/pcap/ "
    #         "-d {{ ds_nodash }} "
    #         "-t TOPS"
    #     ),
    #     skip_on_exit_code=None,
    # )
    # decompress_tops_pcap = BashOperator(
    #     task_id="decompress_top_pcap",
    #     bash_command=("gunzip /tank/iex/pcap/{{ ds_nodash }}_IEXTP1_TOPS1.6.pcap.gz"),
    #     skip_on_exit_code=None,
    # )
    # recompress_top_pcap = BashOperator(
    #     task_id="recompress_top_pcap",
    #     bash_command=(
    #         "zstd --compress -20 --ultra --force "
    #         "-o /tank/iex/pcap/{{ ds_nodash }}_IEXTP1_TOPS1.6.pcap.zst "
    #         "/tank/iex/pcap/{{ ds_nodash }}_IEXTP1_TOPS1.6.pcap"
    #     ),
    #     skip_on_exit_code=None,
    # )
    # delete_top_gz = BashOperator(
    #     task_id="delete_top_gz",
    #     bash_command="rm /tank/iex/pcap/{{ ds_nodash }}_TOPS1.6.pcap.gz",
    # skip_on_exit_code=None,
    # )
    # convert_pcap_to_raw = BashOperator(
    #     task_id="convert_pcap_to_raw",
    #     bash_command=(
    #         "ulimit -n 65536 && convert-pcap "
    #         "--input-path /tank/iex/pcap/{{ ds_nodash }}_IEXTP1_TOPS1.6.pcap.zst "
    #         "--output-path /tank/iex/raw/{{ ds_nodash }}/"
    #     ),
    #     skip_on_exit_code=None,
    # )
    # convert_raw_to_h5 = BashOperator(
    #     task_id="convert_raw_to_h5",
    #     bash_command=(
    #         "python /tank/git/iex-tools/scripts/randoms/gen_h5.py "
    #         "-i /tank/iex/raw/{{ ds_nodash }}/ "
    #         "-o /tank/iex/h5/{{ ds_nodash }}.h5"
    #     ),
    #     skip_on_exit_code=None,
    # )
    # delete_raw_folder = BashOperator(
    #     task_id="delete_top_gz",
    #     bash_command="rm -rf /tank/iex/raw/{{ ds_nodash }}",
    #     skip_on_exit_code=None,
    # )

    (
        download_tops_pcap()
        >> decompress_tops_pcap()
        >> recompress_top_pcap()
        >> convert_pcap_to_raw()
        >> convert_raw_to_h5()
        >> delete_raw_folder()
        >> delete_original_source()
    )
