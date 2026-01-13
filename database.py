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
# Handle specialized connection parameters for SQLAlchemy/psycopg2
# The 'pgbouncer=true' flag is useful for some drivers/clients but causes 'invalid dsn' in psycopg2.
# We remove it for the SQLAlchemy connection string.
if "pgbouncer=true" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("?pgbouncer=true", "").replace("&pgbouncer=true", "")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    # For Supabase Transaction Mode (port 6543), prepared statements should be disabled
    # because pgbouncer doesn't support them well in transaction mode.
    connect_args={
        "options": "-c plan_cache_mode=force_custom_plan"
    }
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
