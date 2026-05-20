from datetime import datetime

from pydantic import BaseModel, Field


class ExecutionStart(BaseModel):
    client_id: int
    periodo: str = Field(min_length=7, max_length=7)


class ExecutionRead(BaseModel):
    id: int
    client_id: int
    periodo: str
    status: str
    started_at: datetime
    finished_at: datetime | None
    log_json: dict[str, object]
    error_details: str | None


class ExecutionDiagnose(BaseModel):
    log_json: dict[str, object]
    status: str | None


class ExecutionXmlsRead(BaseModel):
    total_recebidos: int
    storage_path: str
    status: str
