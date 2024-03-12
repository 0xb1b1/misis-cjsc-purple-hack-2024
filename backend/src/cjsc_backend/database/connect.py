#!/usr/bin/env python3
import psycopg2
from psycopg2 import OperationalError
from loguru import logger


def create_connection(
    db_name: str = None, db_user: str = None,
    db_pass: str = None, db_host: str = None,
    db_port: int | str = None
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
        logger.error(
          f"Error during PostgreSQL connection establishment: '{e}'"
        )
    return connection
