import os
import mysql.connector
from dotenv import load_dotenv


# =========================================================
# LOAD BACKEND .ENV FILE
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

ENV_FILE = os.path.join(
    BASE_DIR,
    ".env"
)

load_dotenv(
    ENV_FILE
)


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():

    return mysql.connector.connect(

        host=os.getenv("DB_HOST"),

        port=int(
            os.getenv(
                "DB_PORT",
                "3306"
            )
        ),

        user=os.getenv("DB_USER"),

        password=os.getenv(
            "DB_PASSWORD",
            ""
        ),

        database=os.getenv("DB_NAME")

    )