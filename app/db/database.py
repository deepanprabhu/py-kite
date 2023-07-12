from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:test1234@mysql:3306/REQUEST_QUEUE"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    isolation_level="READ COMMITTED",
    pool_size=20, max_overflow=0
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except:
        db.rollback()
    finally:
        db.close()