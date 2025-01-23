import time
import random
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2.pool import SimpleConnectionPool
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
    env_file_path = ".env"
    if not os.path.isfile(env_file_path):
        raise FileNotFoundError(
            f"No .env file found at the path: {env_file_path}")
    load_dotenv(dotenv_path=env_file_path)

    # Map each required .env variable to a key in the final DB_CONFIG dictionary.
    # The key on the left is the .env name; the value on the right is how it will appear in DB_CONFIG.
    env_to_config_map = {
        "DB_NAME": "dbname",
        "DB_USER": "user",
        "DB_PASSWORD": "password",
        "DB_HOST": "host",
        "DB_PORT": "port",
        "DB_TABLE_NAME": "table_name"
    }

    DB_CONFIG = {}

    # Validate and build in one loop
    for env_var, config_key in env_to_config_map.items():
        value = os.getenv(env_var)
        if not value:  # Check both None and empty string
            raise ValueError(
                f"The {env_var} environment variable is missing or empty")

        DB_CONFIG[config_key] = value

    # Convert DB_PORT to an integer
    try:
        DB_CONFIG["port"] = int(DB_CONFIG["port"])
    except ValueError:
        raise ValueError("DB_PORT must be a valid integer")

    return DB_CONFIG


def setup_connection_pool():
    """Sets up a connection pool for PostgreSQL."""
    try:
        return SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            dbname=DB_CONFIG["dbname"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"]
        )
    except psycopg2.DatabaseError as e:
        error_message = f"Database error during connection pool setup: {e}"
        print(error_message)
        raise


def create_database():
    """Creates the database if it doesn't exist"""
    try:
        conn = psycopg2.connect(
            dbname="postgres",  # need to connect to a pre-existing Database before creating one
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


def create_table(connection_pool):
    """Creates the table schema"""
    try:
        conn = connection_pool.getconn()
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
    finally:
        if conn:
            connection_pool.putconn(conn)


def insert_data(connection_pool, signal_type, value):
    """Inserts data into the database"""
    try:
        conn = connection_pool.getconn()
        cursor = conn.cursor()
        table_name = DB_CONFIG["table_name"]
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
    finally:
        if conn:
            connection_pool.putconn(conn)


def generate_data(connection_pool):
    """Generates data to be later insereted in the table"""
    while True:
        try:
            # State change every 1-5 seconds
            time.sleep(random.uniform(1, 5))
            insert_data(connection_pool, "state_change", random.choice([0, 1]))

            # Error every 10-30 seconds
            if random.random() < 0.1:
                # The error codes are between 1-100
                insert_data(connection_pool, "error", random.randint(1, 100))

            # Power consumption every 0.01 seconds
            for _ in range(100):  # Simulate 1-second batch
                insert_data(connection_pool, "power",
                            random.uniform(100.0, 500.0))
                time.sleep(0.01)
        except KeyboardInterrupt:
            logging.warning("Data generation stopped.")
            break


if __name__ == "__main__":

    setup_logging()
    DB_CONFIG = get_db_configuration()

    create_database()
    connection_pool = setup_connection_pool()
    create_table(connection_pool)
    generate_data(connection_pool)
    logging.info("Completed executing.")
