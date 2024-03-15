#!/usr/bin/env python3
import psycopg2
from cjsc_backend import config
from loguru import logger
from psycopg2 import OperationalError


def create_connection_with_config():
    """
    Create a connection to the PostgreSQL database using the configuration
    settings.

    :return: connection: The connection object or None.
    """
    return _create_connection(
        db_name=config.DB_NAME,
        db_user=config.DB_USER,
        db_pass=config.DB_PASS,
        db_host=config.DB_HOST,
        db_port=config.DB_PORT,
    )


def _create_connection(
    db_name: str = None,
    db_user: str = None,
    db_pass: str = None,
    db_host: str = None,
    db_port: int | str = None,
):
    """
    Create a connection to the PostgreSQL database.

    :param db_name: str: The name of the database.
    :param db_user: str: The username of the database.
    :param db_pass: str: The password of the database.
    :param db_host: str: The host of the database.
    :param db_port: str: The port of the database.

    :return: connection: The connection object or None.
    """
    try:
        db_port_int = int(db_port)
    except ValueError:
        logger.error("Invalid PostgreSQL port.")
        return None
    connection = None
    try:
        connection = psycopg2.connect(
            database=db_name,
            user=db_user,
            password=db_pass,
            host=db_host,
            port=db_port_int,
        )
        logger.info("Connection to PostgreSQL DB successful.")
    except OperationalError as e:
        logger.error(f"Error during PostgreSQL connection establishment: '{e}'")
    return connection
