from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Get database URL
DATABASE_URL = os.getenv("DATABASE_URL")

# Check if database URL exists
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")

# Create database engine
engine = create_engine(DATABASE_URL)

print("Database engine created successfully")