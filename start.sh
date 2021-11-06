#!/bin/sh

set -e

until mysql -u$RDS_USERNAME -p$RDS_PASSWORD -h$RDS_HOSTNAME -e"CREATE DATABASE IF NOT EXISTS $RDS_DB_NAME"; do
	echo "waiting for db startup"
	sleep 1
done

pipenv run python manage.py migrate
pipenv run python manage.py runserver 0.0.0.0:8000
