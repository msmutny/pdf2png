# Pdf2Png converter

Simple FastAPI web app for converting PDF documents to PNG images, one image per page.


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
<br/>

You can also run only a subset of these 3 services, for example `workers` and `rabbitmq`. 
In such case run the following command
```
docker-compose up workers rabbitmq
```
Then you can start the server manually by running the following command
```
uvicorn app.main:app --host 0.0.0.0 --ssl-certfile certs/cert.pem --ssl-keyfile certs/key.pem --port 10443
```
<br/>

You can also run the `workers` manually using
```
dramatiq app.workers
```
In such case, Windows users need to install the `poppler` dependency manually from [here](https://blog.alivate.com.au/poppler-windows/), see [stackoverflow here](https://stackoverflow.com/questions/18381713/how-to-install-poppler-on-windows)


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

## TODO
  - tests
    - unit
    - integration/e2e
  - Flask instead of FastAPI
  - documentation for /redoc
  - add streaming endpoint (nice to have, not quite sure how to implement using pdf2image)
    - progress bar (extra attribute in response json)
  - Postgres instead of sqlite (nice to have, but not necessary)
