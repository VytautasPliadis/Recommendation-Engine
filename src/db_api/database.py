import sqlalchemy as sql
import sqlalchemy.ext.declarative as declarative
import sqlalchemy.orm as orm
import os

from dotenv import load_dotenv

load_dotenv()


db_url = os.getenv("DB_URL")

engine = sql.create_engine(db_url)

SessionLocal = orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative.declarative_base()
