from sqlmodel import Session, create_engine
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in environment variables")

engine = create_engine(DATABASE_URL, echo=True)


def get_session() -> Session:
    with Session(engine) as session:
        yield session
