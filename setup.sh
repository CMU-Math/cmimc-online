#!/bin/sh

set -eux

if [ ! -f "./.env" ]
then
	cp .env.sample .env
fi

if [ ! -d "./website/problem_graders" ]
then
	cp -nr ./website/example_problem_graders ./website/problem_graders
fi

docker-compose up --build
