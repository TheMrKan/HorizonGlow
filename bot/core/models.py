from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.sql import func
import datetime
import enum

Base = declarative_base()


class Ticket(Base):
    __tablename__ = 'tickets'

    OPENED = 0
    CLOSED = 1

    id: Mapped[int] = mapped_column(primary_key=True)
    topic_id: Mapped[int] = mapped_column(index=True)
    created_at: Mapped[datetime.datetime] = mapped_column(type_=DateTime(timezone=True), server_default=func.now())
    status: Mapped[int] = mapped_column(server_default="0")


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    ticket: Mapped[int] = mapped_column(ForeignKey('tickets.id', ondelete='SET NULL'), server_default=None)
