from sqlalchemy import Column, Integer, String, Boolean, Enum, Date
from banco import Base
import enum

class PrioridadeTarefaEnum(str, enum.Enum):
    urgente = "Urgente"
    alta    = "Alta"
    media   = "Media"
    baixa   = "Baixa"

class CategoriaTarefaEnum(str, enum.Enum):
    trabalho = "Trabalho"
    pessoal  = "Pessoal"
    estudos  = "Estudos"
    saude    = "Saude"

class Tarefas(Base):
    __tablename__ = "tarefas"
    id         = Column(Integer, primary_key=True, index=True)
    user       = Column(String(60), nullable=False)
    titulo     = Column(String(100), nullable=False)
    descricao  = Column(String(300), nullable=False)
    data       = Column(Date, nullable=False)
    concluido  = Column(Boolean, default=False)
    prioridade = Column(Enum(PrioridadeTarefaEnum), nullable=False)
    categoria  = Column(Enum(CategoriaTarefaEnum), nullable=False)

class Users(Base):
    __tablename__ = "users"
    id            = Column(Integer, primary_key=True, index=True)
    username      = Column(String(60), nullable=False)
    senha         = Column(String(30), nullable=False)

class Perfil(Base):
    __tablename__ = "perfil"
    id            = Column(Integer, primary_key=True, index=True)
    nome          = Column(String(60), nullable=False)
    username      = Column(String(60), nullable=False)
    email         = Column(String(60), nullable=False)
    created_at    = Column(Date, nullable=False)