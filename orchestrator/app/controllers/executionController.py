from typing import Any, Dict

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.executionSchema import ExecutionDiagnose, ExecutionRead, ExecutionStart
from app.services.executionService import create_execution, create_execution_diagnose


def create_execution_controller(db: Session, payload: ExecutionStart) -> ExecutionRead:
    try:
        execution = create_execution(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e

    return ExecutionRead.model_validate(
        {
            "id": execution.id,
            "client_id": execution.client_id,
            "periodo": execution.periodo,
            "status": execution.status,
            "started_at": execution.started_at,
            "finished_at": execution.finished_at,
            "log_json": execution.log_json,
            "error_details": execution.error_details,
        }
    )


def create_diagnose_controller(
    db: Session, execution_id: int, log_json: Dict[str, Any]
) -> ExecutionDiagnose:
    try:
        diagnose = create_execution_diagnose(db, execution_id, log_json)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return ExecutionDiagnose.model_validate(
        {"log_json": diagnose.log_json, "status": diagnose.status}
    )
