#!/bin/sh

docker exec -it $(docker ps -q | head -n 1) pipenv run python manage.py createsuperuser
