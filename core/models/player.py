from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import INTEGER, UUID, INET, TEXT, BYTEA, BOOLEAN, INTERVAL
import uuid
from datetime import datetime

from .base import Base

class Player(Base):
    __tablename__ = "player"
    
    player_id: Mapped[int] = mapped_column(nullable=False, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4)
    first_seen_time: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    last_seen_user_name: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    last_seen_time: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    last_seen_address: Mapped[INET] = mapped_column(nullable=False)
    last_seen_hwid: Mapped[BYTEA] = mapped_column(nullable=True)
    last_read_rules: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=True)
    last_seen_hwid_type = mapped_column(nullable=True)