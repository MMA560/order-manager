from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


DATABASE_URL  ="postgresql://postgres.exshzybpmczsxbwzfzep:l5rCvix6BkbCrKHr@aws-0-eu-central-1.pooler.supabase.com:5432/postgres"

enigne = create_engine(DATABASE_URL)

Base = declarative_base()

sessionLocal = sessionmaker(bind= enigne, autoflush=False, autocommit = False)

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally :
        db.close()
