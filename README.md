# PDF2PNG

Simple FastAPI web app for converting PDF documents to PNG images, one image per page.


### How to run the app
Run web server with main app using
```
uvicorn app.api:app --host 0.0.0.0 --ssl-certfile cert.pem --ssl-keyfile key.pem --port 10443
```

Run worker using
```
dramatiq app.worker
```

### TODO
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
- .env template
- fix versions in requirements.txt
- !!!! Flask instead of FastAPI !!!
