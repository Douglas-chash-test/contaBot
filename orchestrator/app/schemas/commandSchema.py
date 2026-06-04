from datetime import datetime

from pydantic import BaseModel


class CommandRead(BaseModel):
    id: int
    execution_id: int
    type: str
    payload: dict[str, object]
    status: str
    sent_at: datetime | None