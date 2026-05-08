from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    cnpj: Mapped[str] = mapped_column(String(14), unique=True, index=True)
    razao_social: Mapped[str] = mapped_column(String(255))
    whatsapp_dest: Mapped[str] = mapped_column(String(32))
    api_key_hash: Mapped[str] = mapped_column(String(255))
    erp_type: Mapped[str] = mapped_column(String(64))
    db_type: Mapped[str] = mapped_column(String(64))
    config_json: Mapped[dict[str, object]] = mapped_column(JSONB)
