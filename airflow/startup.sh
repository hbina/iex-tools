#!/usr/bin/bash

nohup airflow webserver --port 8080 > /usr/share/zfs_pool/airflow/webserver.log &
nohup airflow scheduler > /usr/share/zfs_pool/airflow/schedular.log &
