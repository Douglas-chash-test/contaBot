from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ErrorDictionary(Base):
    __tablename__ = "error_dictionary"

    id: Mapped[int] = mapped_column(primary_key=True)
    error_code: Mapped[str] = mapped_column(String(128), index=True)
    context_json: Mapped[dict[str, object]] = mapped_column(JSONB)
    solution_sql: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(32))
    success_count: Mapped[int] = mapped_column(default=0)
