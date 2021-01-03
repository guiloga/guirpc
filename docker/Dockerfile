FROM python:3.6-alpine

# Metadata
LABEL maintainer="Guillem López Garcia (wyl.loga@gmail.com)"
LABEL version="1.0"
LABEL description="It runs an RPC consumer and setup a producer \
for testing purposes of the guilogacore_rpc package."

# Environment
ENV ROOT_DIR=/root
ENV PACKAGE_NAME=guilogacore_rpc
ENV CMD_MANAGER=$ROOT_DIR/$PACKAGE_NAME/manager.py
ENV CONSUMER_CONFIG_FILEPATH="foobar.ini"
ENV PRODUCER_CONFIG_FILEPATH="foobar_client.ini"
ENV RABBITMQ_URL="guest:guest@rabbitmq:5672"
ENV PYTHONPATH="${PYTHONPATH}:$ROOT_DIR"

# Commnands
WORKDIR $ROOT_DIR

RUN apk update && \
    apk add curl

COPY ./requirements.txt .
RUN pip install --upgrade -U pip && \
    pip install -r requirements.txt && \
    pip install -U pytest flake8

COPY . $ROOT_DIR

RUN python $CMD_MANAGER initconsumer --connect $RABBITMQ_URL foobar
RUN python $CMD_MANAGER initproducer --connect $RABBITMQ_URL foobar_client

ADD ./docker/start_consumer.sh /opt/

CMD ["/bin/sh", "/opt/start_consumer.sh"]
