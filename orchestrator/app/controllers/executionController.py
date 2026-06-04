from typing import Any, Dict, cast

from fastapi import HTTPException, UploadFile, status
from minio import Minio
from sqlalchemy.orm import Session

from app.schemas.executionSchema import (
    ExecutionDiagnose,
    ExecutionFailureCreate,
    ExecutionFailureRead,
    ExecutionRead,
    ExecutionReportsRead,
    ExecutionStart,
    ExecutionXmlsRead,
    ExecutionStatusGet,
)
from app.services.executionService import (
    create_execution,
    create_execution_diagnose,
    fail_execution,
    upload_reports,
    upload_xmls,
    get_execution_status,
)


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


def upload_xmls_controller(
    db: Session, minio_client: Minio, execution_id: int, files: list[UploadFile]
) -> ExecutionXmlsRead:
    try:
        execution = upload_xmls(db, minio_client, execution_id, files)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e

    xmls = cast(dict[str, object], execution.log_json.get("xmls", {}))
    return ExecutionXmlsRead.model_validate(
        {
            "total_recebidos": cast(int, xmls.get("total_recebidos", 0)),
            "storage_path": cast(str, xmls.get("storage_path", "")),
            "status": execution.status,
        }
    )

def upload_reports_controller(
    db: Session, minio_client: Minio, execution_id: int, files: list[UploadFile]
) -> ExecutionReportsRead:
    try:
        execution = upload_reports(db, minio_client, execution_id, files)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e

    reports = cast(dict[str, object], execution.log_json.get("reports", {}))
    return ExecutionReportsRead.model_validate(
        {
            "total_recebidos": cast(int, reports.get("total_recebidos", 0)),
            "storage_path": cast(str, reports.get("storage_path", "")),
            "status": execution.status,
        }
    )

def fail_execution_controller(
    db: Session, 
    execution_id: int, 
    payload: ExecutionFailureCreate
) -> ExecutionFailureRead:
    try:
        execution = fail_execution(db, execution_id, payload)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e

    return ExecutionFailureRead.model_validate(
        {
            "id": execution.id,
            "status": execution.status,
            "finished_at": execution.finished_at,
            "error_details": execution.error_details,
            "log_json": execution.log_json,
        }
    )

def get_execution_status_controller( db:Session, execution_id:int) -> ExecutionStatusGet:
    try:
        execution = get_execution_status(db,execution_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e    
    return ExecutionStatusGet.model_validate(
        {
            "id": execution.id,
            "status": execution.status,
            "started_at": execution.started_at,
            "finished_at": execution.finished_at,
            "error_details": execution.error_details,
            "log_json": execution.log_json,
        }
    )
