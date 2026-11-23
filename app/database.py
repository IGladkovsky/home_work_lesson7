from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = "postgresql+psycopg://postgres:Tiger125@localhost:5432/sqlalchemy_course"

engine = create_engine(DATABASE_URL,echo=True)

SessionLocal = sessionmaker(expire_on_commit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass