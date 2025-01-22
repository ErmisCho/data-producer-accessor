import time
import random
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from datetime import datetime
import os
from dotenv import load_dotenv
import logging


class RaiseOnErrorHandler(logging.Handler):
    """
    A custom logging handler that raises an exception
    when a log with level >= ERROR is emitted.
    """

    def emit(self, record):
        if record.levelno >= logging.ERROR:
            # You can raise a specific exception type (RuntimeError, ValueError, etc.)
            # and possibly include the log message.
            raise RuntimeError(record.getMessage())


def setup_logging():
    """Sets up logging with a configurable log level."""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    logging.basicConfig(
        level=log_level,  # Set log level dynamically
        format="[%(levelname)s] %(asctime)s %(message)s",
        handlers=[
            logging.FileHandler("data_producer.log"),  # Log to a file
            logging.StreamHandler()  # Also log to the console
        ]
    )

    logger = logging.getLogger()
    logger.addHandler(RaiseOnErrorHandler())

    logging.info("Initiating ...")
    logging.info(f"Logging initialized with level: {log_level}")


def get_db_configuration():
    """Gets the user configured Database configuration."""
    load_dotenv(dotenv_path=".env")
    DB_CONFIG = {
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "host": os.getenv("DB_HOST"),
        "port": int(os.getenv("DB_PORT")),
        "table_name": os.getenv("DB_TABLE_NAME")
    }
    return DB_CONFIG


def create_database():
    """Creates the database if it doesn't exist"""
    try:
        conn = psycopg2.connect(
            dbname=DB_CONFIG["dbname"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"])
        conn.autocommit = True
        cursor = conn.cursor()

        # Check if the database exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s", (DB_CONFIG["dbname"],))
        if not cursor.fetchone():
            cursor.execute(f"CREATE DATABASE {DB_CONFIG['dbname']};")
            logging.info(
                f"Database '{DB_CONFIG['dbname']}' created successfully.")
        else:
            logging.info(f"Database '{DB_CONFIG['dbname']}' already exists.")

        cursor.close()
        conn.close()
    except Exception as e:
        logging.error(f"Error creating database: {e}")


def create_table():
    """Creates the table schema"""
    try:
        conn = psycopg2.connect(
            dbname=DB_CONFIG["dbname"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"])
        cursor = conn.cursor()

        table_name = DB_CONFIG["table_name"]

        TABLE_SCHEMA = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id SERIAL PRIMARY KEY,
            signal_type VARCHAR(50) NOT NULL,
            value FLOAT NOT NULL,
            timestamp TIMESTAMP NOT NULL
        );
        """

        cursor.execute(TABLE_SCHEMA)
        conn.commit()
        cursor.close()
        conn.close()
        logging.info(f"Table {table_name} is ready.")
    except Exception as e:
        logging.error(f"Error creating table: {e}")


def insert_data(signal_type, value):
    """Inserts data into the database"""
    try:
        conn = psycopg2.connect(
            dbname=DB_CONFIG["dbname"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"])
        table_name = DB_CONFIG["table_name"]

        cursor = conn.cursor()
        query = f"""
        INSERT INTO {table_name} (signal_type, value, timestamp)
        VALUES (%s, %s, %s);
        """
        cursor.execute(query, (signal_type, value, datetime.now()))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        logging.error(f"Error inserting data: {e}")


def generate_data():
    """Generates data to be later insereted in the table"""
    while True:
        try:
            # State change every 1-5 seconds
            time.sleep(random.uniform(1, 5))
            insert_data("state_change", random.choice([0, 1]))

            # Error every 10-30 seconds
            if random.random() < 0.1:
                # The error codes are between 1-100
                insert_data("error", random.randint(1, 100))

            # Power consumption every 0.01 seconds
            for _ in range(100):  # Simulate 1-second batch
                insert_data("power", random.uniform(100.0, 500.0))
                time.sleep(0.01)
        except KeyboardInterrupt:
            logging.warning("Data generation stopped.")
            break


if __name__ == "__main__":

    setup_logging()
    DB_CONFIG = get_db_configuration()

    create_database()
    create_table()
    generate_data()
    logging.info("Completed executing.")
