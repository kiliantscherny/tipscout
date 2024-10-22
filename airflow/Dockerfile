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

# Create airflow user and group if not exists
RUN groupadd -f airflow && \
    id -u airflow &>/dev/null || useradd -m -d /opt/airflow -g airflow airflow

# Create data directory and set permissions
RUN mkdir -p /opt/airflow/data && \
    chown -R airflow:airflow /opt/airflow/data && \
    chmod -R 775 /opt/airflow/data

# Switch back to airflow user
USER $AIRFLOW_UID

COPY ./airflow/init_airflow.sh /docker-entrypoint-initdb.d/init_airflow.sh