
from sqlalchemy import text
from db import get_engine

try:
    engine = get_engine()

    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("Connection successful!")
        print("Test result:", result.scalar())

except Exception as error:
    print("Database connection failed!")
    print("Reason:", error)
