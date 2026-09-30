from sqlalchemy import create_engine
import os

#DATABASE_URL = "postgresql://postgres:Bhumi1234@localhost:5432/business_analytics1"


DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

print("Database engine created successfully")