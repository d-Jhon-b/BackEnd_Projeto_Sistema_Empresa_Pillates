# src/database/model/base.py

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer

class Base(DeclarativeBase):
    """
    Classe base para todos os modelos ORM.
    Todos os modelos herdarão desta classe.
    """
    pass