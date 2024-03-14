FROM python:3.12-bookworm AS builder

RUN pip install --no-cache-dir poetry==1.4.2

ARG POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /srv/app

COPY pyproject.toml poetry.lock ./

RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --without dev --no-root

FROM python:3.12-slim-bookworm

ENV CJSC_CROSS_APP_SECRET \
    CJSC_BACKEND_PGSQL_HOST \
    CJSC_BACKEND_PGSQL_PORT \
    CJSC_BACKEND_PGSQL_NAME \
    CJSC_BACKEND_PGSQL_USER \
    CJSC_BACKEND_PGSQL_PASS \
    CJSC_BACKEND_JWT_SECRET_KEY \
    CJSC_BACKEND_JWT_ACCESS_EXPIRATION_DAYS

WORKDIR /srv/app

ENV VIRTUAL_ENV=/srv/app/.venv \
    PATH="/srv/app/.venv/bin:$PATH" \
    PYTHONPATH=/srv/app/src

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

WORKDIR /srv/app/src

COPY ./src ./

ENTRYPOINT ["python", "-m", "cjsc_backend.main"]
