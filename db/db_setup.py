from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from contextlib import contextmanager


DATABASE_URL = "sqlite:///exam_bot.db"
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)

# initializing
# Base.metadata.create_all(engine)
# print("Database initialized!")


@contextmanager
def get_db_session():
    session = SessionLocal()
    try:
        yield session  # Yield the actual session object
    finally:
        session.close()  # Ensure the session is properly closed
