FROM python:3.7-slim-buster

WORKDIR /app

RUN apt-get update && \
	DEBIAN_FRONTEND=noninteractive apt-get install -qy mariadb-client libmariadbclient-dev gcc make && \
	apt-get clean && \
	rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN pip install --no-cache-dir pipenv

COPY Pipfile Pipfile.lock ./
RUN pipenv install

COPY . .

CMD [ "./start.sh" ]
