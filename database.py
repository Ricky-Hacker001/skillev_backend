from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ⚠️ REPLACE 'YOUR_REAL_PASSWORD' WITH THE PASSWORD YOU USE FOR PGADMIN
# Example: "postgresql://postgres:root@localhost:5432/skillev"
password = "Ricky@!12"

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:123456@localhost:5432/skillev"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()