#!/bin/bash
set -e

# Commands to set correct permissions
chown -R airflow:airflow /opt/airflow/data
chmod -R 775 /opt/airflow/data