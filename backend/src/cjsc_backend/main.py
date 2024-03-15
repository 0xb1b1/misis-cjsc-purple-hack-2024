#!/usr/bin/env python3
import sys

import sentry_sdk
import socketio
import uvicorn
from cjsc_backend import config
from cjsc_backend.routers.http.auth import router as auth_router
from cjsc_backend.routers.http.debug import router as debug_router
from cjsc_backend.routers.http.messages import router as msg_router
from cjsc_backend.routers.http.root import router as root_router
from cjsc_backend.routers.ws.messages import sio as ws_msg_sio
from cjsc_backend.setup import cors
from fastapi import FastAPI
from loguru import logger
from sentry_sdk.integrations.loguru import LoguruIntegration


def run() -> None:
    sentry_sdk.init(
        dsn="https://504cad1b6c754661b2fb793b9162359c@glitchtip.seizure.icu/2",
        enable_tracing=True,
        integrations=[
            LoguruIntegration(),
        ],
    )
    logger.info("Initialized Sentry.")

    app = FastAPI(
        title="CJSC Backend",
        description="Backend solution for CJSC Team",
        version="0.0.1",
    )
    cors.set_cors_policy(app)

    app.include_router(debug_router)
    app.include_router(root_router)
    app.include_router(msg_router)
    app.include_router(auth_router)

    combined_asgi_app = socketio.ASGIApp(ws_msg_sio, app)

    logger.info(f"Starting webserver at \
`{config.WEBSERVER_HOST}:{config.WEBSERVER_PORT}...`")
    uvicorn.run(
        combined_asgi_app, host=config.WEBSERVER_HOST, port=config.WEBSERVER_PORT
    )


if __name__ == "__main__":
    run()
    sys.exit(0)
