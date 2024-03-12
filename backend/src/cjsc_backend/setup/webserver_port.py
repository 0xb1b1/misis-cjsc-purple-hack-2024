#!/usr/bin/env python3


def validate_webserver_port(webserver_port: int | str) -> (int, bool):
    """
    This function validates the logging level and,
    if it's valid, returns the string in the correct
    (upper-case) format. If webserver_port is NoneType,
    defaults to 8080.

    Args:
        webserver_port (int | str): Webserver port value.

    Returns:
        (int, bool): Webserver port and if it's default.

    Raises:
        ValueError: The webserver port integer in not in bounds.
    """

    if webserver_port is None:
        return (8080, True)

    if isinstance(webserver_port, str):
        webserver_port = int(webserver_port)

    if not 1 <= webserver_port <= 65535:
        raise ValueError("Webserver port value is outside of defined bounds.")

    return (webserver_port, False)
