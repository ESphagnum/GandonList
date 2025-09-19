from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import (
    INTEGER,
    UUID,
    INET,
    TEXT,
    BYTEA,
    BOOLEAN,
    INTERVAL,
)
import uuid
from datetime import datetime, timedelta
import ipaddress

from .base import Base


class ServerBan(Base):
    __tablename__ = "server_ban"

    server_ban_id: Mapped[int] = mapped_column(
        INTEGER, nullable=False, primary_key=True
    )
    player_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("player.user_id"), nullable=True
    )
    address: Mapped[ipaddress.IPv4Address] = mapped_column(INET, nullable=True)
    ban_time: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    expiration_time: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=True
    )
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    banning_admin: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("player.user_id"), nullable=True
    )
    hwid: Mapped[bytes] = mapped_column(BYTEA, nullable=True)
    exempt_flags: Mapped[int] = mapped_column(INTEGER, nullable=False)
    auto_delete: Mapped[bool] = mapped_column(BOOLEAN, nullable=False)
    hidden: Mapped[bool] = mapped_column(BOOLEAN, nullable=False)
    last_edited_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=True
    )
    last_edited_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("player.user_id"), nullable=True
    )
    playtime_at_note: Mapped[timedelta] = mapped_column(INTERVAL, nullable=False)
    round_id: Mapped[int] = mapped_column(INTEGER, nullable=True)
    severity: Mapped[int] = mapped_column(INTEGER, nullable=False)
    hwid_type: Mapped[int] = mapped_column(INTEGER, nullable=True)
