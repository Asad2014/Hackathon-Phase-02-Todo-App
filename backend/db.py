from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from config import settings
import urllib.parse

# Use the database URL from settings and ensure it uses async driver
DATABASE_URL = settings.DATABASE_URL

# Parse the URL to handle parameters properly for asyncpg compatibility
if DATABASE_URL.startswith("postgresql://"):
    # Parse the URL
    parsed = urllib.parse.urlparse(DATABASE_URL)

    # Handle query parameters for asyncpg compatibility
    query_params = urllib.parse.parse_qs(parsed.query)

    # Remove parameters that are not compatible with asyncpg
    # asyncpg handles SSL automatically and differently than psycopg2
    filtered_params = {k: v[0] if isinstance(v, list) and len(v) == 1 else v
                      for k, v in query_params.items()
                      if k.lower() not in ['sslmode', 'sslcert', 'sslkey', 'sslrootcert']}

    # Reconstruct query string without incompatible params
    if filtered_params:
        new_query = urllib.parse.urlencode(filtered_params, doseq=True)
    else:
        new_query = ''

    # Reconstruct the URL with the new protocol and filtered parameters
    DATABASE_URL = urllib.parse.urlunparse((
        'postgresql+asyncpg',
        parsed.netloc,
        parsed.path,
        parsed.params,
        new_query,  # query string without sslmode
        parsed.fragment
    ))
else:
    # If it's already in the right format, just ensure it uses asyncpg
    if "postgresql+asyncpg://" not in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Create async engine with proper connection pool settings to prevent connection closure issues
engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Validates connections before use
    pool_recycle=300,    # Recycle connections after 5 minutes
)

# Create session maker
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_session():
    async with AsyncSessionLocal() as session:
        yield session

async def create_db_and_tables():
    # Import models to register them with SQLModel before creating tables
    import models  # Import the models module to register table definitions

    async with engine.begin() as conn:
        # Drop all tables first to ensure schema is up-to-date (development only!)
        await conn.run_sync(SQLModel.metadata.drop_all)
        # Create all tables with the updated schema
        await conn.run_sync(SQLModel.metadata.create_all)