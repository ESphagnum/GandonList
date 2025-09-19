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
    VARCHAR,
)
import uuid
from datetime import datetime, timedelta
import ipaddress

from .base import Base


class AdminNotes(Base):
    __tablename__ = "admin_notes"

    admin_notes_id: Mapped[int] = mapped_column(
        INTEGER, nullable=False, primary_key=True
    )
    round_id: Mapped[int] = mapped_column(INTEGER, nullable=True)
    player_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), default=uuid.uuid4, nullable=True
    )
    message: Mapped[str] = mapped_column(VARCHAR(2000), nullable=False)

    created_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), default=uuid.uuid4, nullable=True
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    last_edited_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), default=uuid.uuid4, nullable=True
    )
    last_edited_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    deleted: Mapped[bool] = mapped_column(BOOLEAN, nullable=False)
    deleted_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), default=uuid.uuid4, nullable=True
    )
    deleted_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=True
    )

    secret: Mapped[bool] = mapped_column(BOOLEAN, nullable=False)
    expiration_time: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=True
    )
    severity: Mapped[int] = mapped_column(INTEGER, nullable=False)
    playtime_at_note: Mapped[timedelta] = mapped_column(INTERVAL, nullable=False)
