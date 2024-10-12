FROM apache/airflow:2.8.3

ENV AIRFLOW_HOME=/opt/airflow

USER root
RUN apt-get update -qq && apt-get install vim -qqq && apt-get install -y gosu -qqq

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -v

SHELL ["/bin/bash", "-o", "pipefail", "-e", "-u", "-x", "-c"]

WORKDIR $AIRFLOW_HOME

COPY ./airflow/scripts scripts
RUN chmod +x scripts

# Create data directory and set permissions
RUN mkdir -p /opt/airflow/data && \
    chown -R airflow:0 /opt/airflow/data && \
    chmod 775 /opt/airflow/data

USER airflow