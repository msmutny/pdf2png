# Pdf2Png converter

Simple FastAPI web app for converting PDF documents to PNG images, one image per page.


## How to build and run the project

### Build
From the project root folder run the following command
```
docker-compose build
```

### Run
Project consists of 3 services:
  - `api`
  - `workers`
  - `rabbitmq`

You can run all 3 services from the project root folder using the following command
```
docker-compose up
```
<br/>

You can also run only a subset of these 3 services, for example `workers` and `rabbitmq`. 
In such case run the following command
```
docker-compose up workers rabbitmq
```
Then you can start the server manually by running the following command
```
uvicorn app.api:app --host 0.0.0.0 --ssl-certfile certs/cert.pem --ssl-keyfile certs/key.pem --port 10443
```
<br/>

You can also run the `worker` manually using
```
dramatiq app.worker
```
In such case, Windows users need to install the `poppler` dependency manually from [here](https://blog.alivate.com.au/poppler-windows/), see [stackoverflow here](https://stackoverflow.com/questions/18381713/how-to-install-poppler-on-windows)


## TODO
  - tests
    - unit
    - e2e
  - Postgres instead of sqlite
  - structure project nicely
  - use best practices
  - documentation for /redoc
  - readme
  - handle errors
    - status codes
    - err messages
  - logging
  - admin API
  - fix versions in requirements.txt
  - add streaming endpoint
    - progress bar (extra attribute in response json)
  - crop PNG to 1200x1600 px
  - !!!! Flask instead of FastAPI !!!
