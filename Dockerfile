FROM python:3.9-slim
EXPOSE 10443

RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2 \
	&& apt-get -y install poppler-utils

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY *.pem ./
COPY app/ app

CMD uvicorn app.api:app --host 0.0.0.0 --ssl-certfile cert.pem --ssl-keyfile key.pem --port 10443
