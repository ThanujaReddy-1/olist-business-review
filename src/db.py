
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Load database details from the .env file
load_dotenv()

# Create a function to connect to PostgreSQL
def get_engine():
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    database = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")

    # Build the PostgreSQL connection URL
    url = (
        f"postgresql+psycopg2://{user}:{password}"
        f"@{host}:{port}/{database}"
    )

    # Create and return the database engine
    engine = create_engine(url)

    return engine
