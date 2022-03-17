#!/bin/sh

docker-compose exec cmimc pipenv run python manage.py createsuperuser
