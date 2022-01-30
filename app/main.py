import warnings

from fastapi import FastAPI

from app.api import public, admin
from app.db import create_db_and_tables


tags_metadata = [{"name": "Public"}, {"name": "Admin"}]
app = FastAPI(openapi_tags=tags_metadata)

app.include_router(public.router)
app.include_router(admin.router)

# Temporary workaround for #https://github.com/tiangolo/sqlmodel/issues/189
warnings.filterwarnings("ignore", ".*Class SelectOfScalar will not make use of SQL compilation caching.*")


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
