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
COPY certs/ certs

# uncomment this line if you're using Flask
CMD FLASK_APP=app.main_flask flask run --host 0.0.0.0 --port 10443 --cert=certs/cert.pem --key=certs/key.pem

# uncomment this line if you're using FastAPI
# CMD uvicorn app.main:app --host 0.0.0.0 --ssl-certfile certs/cert.pem --ssl-keyfile certs/key.pem --port 10443
