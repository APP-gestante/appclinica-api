from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# Criar a engine assíncrona
engine = create_async_engine(
    settings.sqlalchemy_database_uri,
    echo=False, # Set to True para debugar SQL
    future=True,
    pool_pre_ping=True,
    connect_args={"ssl": "require"},
)

# Criar o construtor de sessões
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()
