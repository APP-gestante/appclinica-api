from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

# Determinar modo SSL: require apenas se for Supabase/Production
ssl_mode = "require" if "supabase" in settings.sqlalchemy_database_uri else False

# Criar a engine assíncrona
engine = create_async_engine(
    settings.sqlalchemy_database_uri,
    echo=False,  # Set to True para debugar SQL
    future=True,
    pool_pre_ping=True,
    connect_args={"ssl": ssl_mode},
)

# Criar o construtor de sessões
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()
