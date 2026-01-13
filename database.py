import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in .env file")

# Supabase Transaction Pooler (pgbouncer) compatibility
# If using port 6543, Supabase uses pgbouncer.
# We might need to disable server-side cursors or prepared statements if running in transaction mode,
# though standard SQLAlchemy usage is usually fine.
# adding pool_pre_ping to ensure connections are alive.
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    # For transaction poolers, sometimes 'execution_options={"isolation_level": "AUTOCOMMIT"}' is suggested for simple queries,
    # but for ORM usage we usually want transactions.
    # Supabase docs suggest basic connection is fine if using the session pooler.
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initializes the database tables."""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency for getting DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
