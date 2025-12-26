from sqlalchemy import String, Text, DateTime, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from db import Base

class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    filename: Mapped[str] = mapped_column(String(512))
    mime: Mapped[str] = mapped_column(String(128), default="")
    gcs_uri: Mapped[str] = mapped_column(String(1024))
    status: Mapped[str] = mapped_column(String(64), default="RECEIVED")

    text: Mapped[str | None] = mapped_column(Text, nullable=True)
    entities_json: Mapped[str] = mapped_column(Text, default="[]")
    tags_json: Mapped[str] = mapped_column(Text, default="[]")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), server_default=func.now()
    )

    __table_args__ = (
        Index("idx_doc_filename", "filename"),
        Index("idx_doc_status", "status"),
    )
