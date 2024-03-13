#!/usr/bin/env python3

import os
import sys
from loguru import logger
from fastapi_jwt import JwtAccessBearer
from datetime import timedelta

from cjsc_backend.setup import webserver_port

is_run_fatal = False

# if file ./dev.flag exists, load_dotenv()
if os.path.isfile("./dev.flag"):
    logger.warning("Loading environment variables from .env file... (`dev.flag` detected)")
    from dotenv import load_dotenv
    load_dotenv()
    logger.info("Loaded environment variables from .env file.")

WEBSERVER_HOST: str = os.getenv(
    "CJSC_BACKEND_WEBSERVER_HOST",
    "0.0.0.0"
)
logger.info(f"Webserver host set to `{WEBSERVER_HOST}`")

WEBSERVER_PORT, IS_WEBSERVER_PORT_DEFAULT = webserver_port.validate_webserver_port(  # noqa: E501
    os.getenv("CJSC_BACKEND_WEBSERVER_PORT")
)
logger.info(f"Webserver port set to `{WEBSERVER_PORT}`")

# JWT
# Authentication (oauth2//jwt)
JWT_SECRET_KEY = os.getenv("CJSC_BACKEND_JWT_SECRET_KEY", "")
JWT_ACCESS_EXPIRATION_MINUTES = int(
    os.getenv(
        "CJSC_BACKEND_JWT_ACCESS_EXPIRATION_MINUTES",
        "30",
    )
)

if JWT_SECRET_KEY == "":
    logger.critical("JWT Secret key is not specified.")
    is_run_fatal = True

jwt_ac = JwtAccessBearer(
    secret_key=JWT_SECRET_KEY,
    auto_error=True,
    access_expires_delta=timedelta(JWT_ACCESS_EXPIRATION_MINUTES),
)

# PostgreSQL
DB_HOST = os.getenv("CJSC_BACKEND_PGSQL_HOST")
DB_PORT = os.getenv("CJSC_BACKEND_PGSQL_PORT")
DB_NAME = os.getenv("CJSC_BACKEND_PGSQL_NAME")
DB_USER = os.getenv("CJSC_BACKEND_PGSQL_USER")
DB_PASS = os.getenv("CJSC_BACKEND_PGSQL_PASS")
if not DB_NAME or not DB_USER or not DB_PASS or not DB_HOST or not DB_PORT:
    logger.critical("Some or all PostgreSQL connection parameters not provided")
    is_run_fatal = True

# Chat management
CHAT_EXPIRY_MINUTES = int(
    os.getenv(
        "CJSC_BACKEND_CHAT_EXPIRY_MINUTES",
        "20",
    )
)

########
if is_run_fatal:
    logger.critical("Setup failed. Exiting.")
    sys.exit(1)
