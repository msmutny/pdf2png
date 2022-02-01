import warnings
from dataclasses import dataclass

from flask import Flask

from app.config.db import create_db_and_tables
from app.routes import public, admin

app = Flask(__name__)
app.register_blueprint(public.public_route)
app.register_blueprint(admin.admin_route)


# Temporary workaround for #https://github.com/tiangolo/sqlmodel/issues/189
warnings.filterwarnings("ignore", ".*Class SelectOfScalar will not make use of SQL compilation caching.*")


@dataclass
class Config:
    FLASK_PYDANTIC_VALIDATION_ERROR_STATUS_CODE: int = 422


app.config.from_object(Config)


@app.before_first_request
def on_startup():
    create_db_and_tables()
