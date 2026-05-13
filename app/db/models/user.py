from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class User(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(200), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(200))
