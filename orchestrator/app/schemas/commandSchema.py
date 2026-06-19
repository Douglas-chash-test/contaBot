from datetime import datetime

from pydantic import BaseModel, Field


class CommandRead(BaseModel):
    id: int
    execution_id: int
    type: str
    payload: dict[str, object]
    status: str
    sent_at: datetime | None

class CommandResultCreate(BaseModel):
    success: bool
    result: dict[str, object] = Field(default_factory=dict)
    error_message: str | None = None

class CommandResultRead(BaseModel):
    id: int
    execution_id: int
    status: str
    result_json: dict[str, object] | None
    executed_at: datetime | None
