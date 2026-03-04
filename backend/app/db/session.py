from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

engine = create_engine(os.getenv("DATABASE_URL"))

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)