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

class ExecutionReportsRead(BaseModel):
    total_recebidos: int
    storage_path: str
    status: str

class ExecutionFailureRead(BaseModel):
    id: int
    status: str
    finished_at: datetime 
    error_details: str | None
    log_json: dict[str, object]

class ExecutionFailureCreate(BaseModel):
    error_code: str | None = None
    message: str 
    details: dict[str, object] = Field(default_factory=dict)


class ExecutionStatusGet(BaseModel):
    id: int
    status: str
    started_at: datetime
    finished_at: datetime | None
    error_details: str | None
    log_json: dict[str, object]
