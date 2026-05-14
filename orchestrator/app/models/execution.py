from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Execution(Base):
    __tablename__ = "executions"
    __table_args__ = (Index("ix_executions_client_periodo", "client_id", "periodo"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id", ondelete="CASCADE"))
    periodo: Mapped[str] = mapped_column(String(7))
    status: Mapped[str] = mapped_column(String(32), index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    log_json: Mapped[dict[str, object]] = mapped_column(JSONB)
    error_details: Mapped[str | None] = mapped_column(Text)
