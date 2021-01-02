#!/bin/sh

STATUS=000;
while [ $STATUS != 200 ];
do
  tms=$(date '+%Y-%m-%d %H:%M:%S');
  echo "${tms} -> Waiting for rabbitmq server to finish start up (sleeping 15) ..";
  sleep 15;
  STATUS=$(curl -o /dev/null -s -w "%{http_code}\n" rabbitmq:15672);
done;

python "${CMD_MANAGER}" runconsumer