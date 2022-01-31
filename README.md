# Pdf2Png converter

Simple FastAPI web app for converting PDF documents to PNG images, one image per page. \
It uses rabbitmq message broker to offload the workload to workers running in a separate container.


## How to build and run Pdf2Png converter

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


## How to use Pdf2Png converter
Pdf2Png converted is accessible via REST API. If you run it using `docker-compose up`, it's accessible on `localhost`, port `10443`.
Note that since it provides a self-signed certificate, connection to it will be treated as insecure and depending on how to access it
(either via `curl` or web browser or REST client like [Postman](https://www.postman.com/product/rest-client/)) you need to allow exceptions.

### Endpoints
  - `POST /documents`
  - `GET /documents/{id}`
  - `GET /documents/{id}/pages/{page_number}`

For full specification see OpenAPI spec `https://localhost:10443/openapi.json`

### Swagger
```
https://localhost:10443/docs
```

### Curl
#### POST /documents
```
curl -X 'POST' -k \
  'https://localhost:10443/documents' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@tests/resouces/perspective_lab.pdf;type=application/pdf'
```

<br/>

#### GET /documents/{id}
```
curl -X 'GET' -k \
  'https://localhost:10443/documents/{id}' \
  -H 'accept: application/json'
```
- replace `{id}` by the real document id

<br/>

#### GET /documents/{id}/pages/{page_number}
```
curl -X 'GET' -k \
  'https://localhost:10443/documents/{id}/pages/{page_number}' \
  -H 'accept: image/png' \
  --output {output_file}
```
- replace `{id}` by the real document id
- replace `{page_number}` by the page number you want to see
- replace `{output_file}` by the output file path to store the resulting image in PNG format

<br/>

### For developers
You can also mimic running the `workers` and/or `api` service manually.
- In order to start a web server with the main app, run the following command
```
uvicorn app.main:app --host 0.0.0.0 --ssl-certfile certs/cert.pem --ssl-keyfile certs/key.pem --port 10443
```

- For running the workers, use the command below. Note that it needs these dependencies:
  - `poppler-utils`
    - Linux `sudo apt-get install -y poppler-utils`
    - Windows download from  [here](https://blog.alivate.com.au/poppler-windows/), see [stackoverflow here](https://stackoverflow.com/questions/18381713/how-to-install-poppler-on-windows)
```
dramatiq app.workers
```
<br/>

#### Running the tests
Use the following command from project root folder to run the tests:
```
pytest -v .
```
You'll need 2 more extra dependencies -- `pytest` and `requests` -- see `requirements-dev.txt`


## TODO
  - Flask instead of FastAPI
  - documentation for /redoc
  - add streaming endpoint (nice to have, not quite sure how to implement using pdf2image)
    - progress bar (extra attribute in response json)
  - Postgres instead of sqlite (nice to have, but not necessary)
