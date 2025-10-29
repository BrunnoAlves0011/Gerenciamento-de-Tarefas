from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL de conexão com SQLite
DATABASE_URL = "sqlite:///./banco.db"

# Cria o motor de conexão
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
# Cria a fábrica de sessões
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe base para os modelos
Base = declarative_base()
