import json
import logging
import os
import sqlite3
import time
from contextlib import closing
from pathlib import Path


def query_books_database(
    sql_query: str, db_url: str = "books_data.db"
) -> list[dict]:
    """
    Execute a read-only SQL query on the books database and return the results.

    Args:
        sql_query (str): SQL query string to execute.
        db_url (str): URL to the database file, defaults to "data/books_data.db".

    Returns:
        list[dict[str, str | float | int]]: A list of rows as dictionaries
    """
    with closing(sqlite3.connect(f"file:{db_url}?mode=ro", uri=True)) as connection:
        connection.row_factory = lambda cursor, row: {
            col[0]: row[i] for i, col in enumerate(cursor.description)
        }
        with closing(connection.cursor()) as cursor:
            rows = cursor.execute(sql_query).fetchall()
    return rows


def handle_function_calls(
    function_map: dict, response_message, thread: list
) -> list | None:
    """
    Handle function tool calls and map them to actual function executions.

    Arguments:
        function_map (dict): A dictionary mapping function names to function objects.
        response_message: The message containing tool call information.
        thread (list): List to append results of function calls.

    Returns:
        list: Updated list of messages.

    Raises:
        ValueError: If no tool calls are present in the response message.
        KeyError: If a function mapping is not found.
    """
    if not response_message.tool_calls:
        raise ValueError("No tool calls found in the response message.")

    for tool_call in response_message.tool_calls:
        function_name = tool_call.function.name
        if function_name in function_map:
            function_args = json.loads(tool_call.function.arguments)
            print(f"Function arguments: {function_args}")

            function_to_call = function_map[function_name]
            try:
                function_response = function_to_call(**function_args)
            except Exception as e:
                function_response = str(e)

            thread.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": str(function_response),
                }
            )
            return thread
        else:
            print(f"Function {function_name} not found.")
            raise KeyError(f"Function {function_name} not found in function map.")


def create_logger(logger_name: str, log_file: str, log_level: str) -> logging.Logger:
    """
    Create and configure a logger with specified name, log file, and log level.

    Arguments:
        logger_name (str): Name of the logger.
        log_file (str): Path to the log file.
        log_level (str): Logging level as a string (e.g., 'INFO', 'DEBUG').

    Returns:
        logging.Logger: Configured logger object.
    """
    LOG_FORMAT = "[%(asctime)s | %(name)s | %(levelname)s | %(funcName)s | %(message)s]"
    log_level = getattr(logging, log_level.upper())

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(console_handler)

    return logger


def log_execution_time(logger: logging.Logger):
    """
    Decorator factory to log the execution time of a function using a specified logger.

    Arguments:
        logger (logging.Logger): Logger object used for logging.

    Returns:
        function: A decorator that logs the execution time of the wrapped function.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            logger.info(f"Executing {func.__name__} took {execution_time:.4f} seconds")
            return result

        return wrapper

    return decorator
