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
RUN mkdir -p /opt/airflow/data && chown -R $AIRFLOW_UID:0 /opt/airflow/data

# Ensure the airflow user has read/write permissions
RUN chmod 775 /opt/airflow/data
RUN touch /opt/airflow/data/tipsterdeals.duckdb && chmod 664 /opt/airflow/data/tipsterdeals.duckdb && chown $AIRFLOW_UID:0 /opt/airflow/data/tipsterdeals.duckdb

USER $AIRFLOW_UID