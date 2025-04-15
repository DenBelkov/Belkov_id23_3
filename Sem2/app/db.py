from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
engine = create_engine("sqlite:///auth1.db")
SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)
Base.metadata.create_all(engine)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()