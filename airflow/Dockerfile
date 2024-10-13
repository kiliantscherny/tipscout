FROM apache/airflow:2.8.3

ENV AIRFLOW_HOME=/opt/airflow

USER root
RUN apt-get update -qq && apt-get install vim -qqq && apt-get install -y gosu -qqq

COPY requirements.txt .

USER airflow
RUN pip install --no-cache-dir -r requirements.txt -v

SHELL ["/bin/bash", "-o", "pipefail", "-e", "-u", "-x", "-c"]

USER root
WORKDIR $AIRFLOW_HOME

COPY ./airflow/scripts scripts
RUN chmod +x scripts

# Create data directory
RUN mkdir -p /opt/airflow/data 

USER $AIRFLOW_UID 

COPY ./airflow/init_airflow.sh /docker-entrypoint-initdb.d/init_airflow.sh