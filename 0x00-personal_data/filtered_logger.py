#!/usr/bin/env python3
""" Filtered logger Module """
import re
import logging
import os
import mysql.connector
from typing import List


class RedactingFormatter(logging.Formatter):
    """ RedactingFormatter class """

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        super(RedactingFormatter, self).__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """ Format the specified log record """
        message = super().format(record)
        for field in self.fields:
            message = re.sub(
                rf'{field}=.+?{self.SEPARATOR}',
                f'{field}={self.REDACTION}{self.SEPARATOR}',
                message
            )
        return message


PII_FIELDS: List[str] = ['name', 'email', 'phone', 'ssn', 'password']


def filter_datum(fields: list, redaction: str, message: str,
                 separator: str) -> str:
    """ Returns the log message with obfuscated fields """
    return re.sub(r'(?<={}=).*?(?={})'.format(separator, separator),
                  redaction, message)


def get_logger() -> logging.Logger:
    """ Returns the logger object """
    logger = logging.getLogger('user_data')
    logger.setLevel(logging.INFO)
    logger.propagate = False

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)

    formatter = RedactingFormatter(list(PII_FIELDS))
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    return logger


def get_db() -> mysql.connector.connection.MySQLConnection:
    """ Returns the connection to the database """
    db_connect = mysql.connector.connect(
        user=os.getenv('PERSONAL_DATA_DB_USERNAME', 'root'),
        password=os.getenv('PERSONAL_DATA_DB_PASSWORD', ''),
        host=os.getenv('PERSONAL_DATA_DB_HOST', 'localhost'),
        database=os.getenv('PERSONAL_DATA_DB_NAME')
    )
    return db_connect


def main() -> None:
    """ Retrieves the data from the database and logs it """
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users")
    logger = get_logger()
    for row in cursor:
        message = "; ".join([
            f"{field}={str(value)}"
            for field, value
            in zip(cursor.column_names, row)])
        logger.info(message)
    cursor.close()
    db.close()


if __name__ == "__main__":
    main()
