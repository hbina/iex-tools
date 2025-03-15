#!/usr/bin/fish

# set -x
echo "Killing airflow processes..."
sudo pkill -f airflow
sleep 5
echo "Listing airflow processes, it should be empty..."
pgrep -af airflow
echo "Starting the processes back up..."
nohup airflow webserver --port 8080 > webserver.log &
sleep 1
nohup airflow scheduler > scheduler.log &
