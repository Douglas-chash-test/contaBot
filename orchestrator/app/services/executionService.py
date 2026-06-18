from datetime import UTC, datetime
from typing import Any, Dict

from fastapi import UploadFile
from minio import Minio
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from app.models.execution import Execution
from app.schemas.executionSchema import ExecutionFailureCreate, ExecutionStart


def create_execution(db: Session, payload: ExecutionStart) -> Execution:

    valida_client = db.execute(
        text("""Select id 
        from clients where 
        clients.id = :client_id"""),
        {"client_id": payload.client_id},
    ).scalar_one_or_none()

    if valida_client is None:
        raise ValueError("O client_id informado não existe na base de dados")

    execution = Execution(
        client_id=payload.client_id,
        periodo=payload.periodo,
        status="started",
        started_at=datetime.now(UTC),
        log_json={},
    )
    db.add(execution)
    db.commit()
    db.refresh(execution)
    return execution


def create_execution_diagnose(
    db: Session, execution_id: int, log_json: Dict[str, Any]
) -> Execution:
    execution = db.get(Execution, execution_id)
    if not execution:
        raise ValueError("Execução não encontrada")

    log_atual = execution.log_json or {}
    log_atual["diagnostico"] = log_json
    execution.log_json = log_atual
    execution.status = "em_progresso"
    db.commit()
    db.refresh(execution)
    return execution


def upload_xmls(
    db: Session, minio_client: Minio, execution_id: int, file: list[UploadFile]
) -> Execution:
    execution = db.get(Execution, execution_id)
    if not execution:
        raise ValueError("Execução não encontrada")
    if execution.status != "em_progresso":
        raise ValueError("Execução não está em progresso")

    diagnostico = execution.log_json.get("diagnostico", {})
    esperado = diagnostico.get("total_notas")
    if esperado != len(file):
        raise ValueError(
            f"Quantidade de XMLs recebidos ({len(file)}) "
            f"não corresponde ao total de notas ({esperado})"
        )

    for files in file:
        filename = files.filename or ""
        if not filename.endswith(".xml"):
            raise ValueError(f"Arquivo {filename} não é um XML")

    storage_path = f"{execution.client_id}/{execution.periodo}/xmls/"

    for files in file:
        minio_client.put_object(
            bucket_name="contabot",
            object_name=f"{storage_path}{files.filename}",
            data=files.file,
            length=-1,
            part_size=10 * 1024 * 1024,
        )
    log_atual = execution.log_json or {}
    log_atual["xmls"] = {"total_recebidos": len(file), "storage_path": storage_path}
    execution.log_json = log_atual
    flag_modified(execution, "log_json")
    db.commit()
    db.refresh(execution)
    return execution

def upload_reports(
        db: Session,
        minio_client: Minio, 
        execution_id: int, 
        file: list[UploadFile],
        ) -> Execution:
    execution = db.get(Execution, execution_id)
    if not execution:
        raise ValueError("Execução não encontrada")
    log_atual = execution.log_json or {}
    if execution.status != "em_progresso" or "xmls" not in log_atual:
        raise ValueError("Execução não está em progresso ou xml não foi enviado")

    storage_path = f"{execution.client_id}/{execution.periodo}/reports/"

    for files in file:
        filename = files.filename or ""
        if not (filename.endswith(".pdf") or filename.endswith(".txt")):
            raise ValueError(f"Arquivo {filename} não é um PDF ou TXT")

        minio_client.put_object(
            bucket_name="contabot",
            object_name=f"{storage_path}{files.filename}",
            data=files.file,
            length=-1,
            part_size=10 * 1024 * 1024,
        )
    log_atual["reports"] = {"total_recebidos": len(file), "storage_path": storage_path}
    execution.log_json = log_atual
    execution.status = "ready_for_validation"
    flag_modified(execution, "log_json")
    db.commit()
    db.refresh(execution)
    return execution

def fail_execution(db: Session, 
                   execution_id: int, 
                   payload: ExecutionFailureCreate, 
                   ) -> Execution:
    
    execution = db.get(Execution, execution_id)
    if not execution:
        raise ValueError("Execução não encontrada")
    if execution.status in ["failed", "completed" , "ready_for_validation"]:
        raise ValueError("Execução ja concluida!!")
    
    log_atual = execution.log_json or {}
    failure_payload = payload.model_dump()

    log_atual["failure"] = {
        **failure_payload,
        "reported_at": datetime.now(UTC).isoformat()
    }


    execution.status = "failed"
    execution.finished_at = datetime.now(UTC)
    execution.error_details = payload.message
    execution.log_json = log_atual

    flag_modified(execution, "log_json")
    db.commit()
    db.refresh(execution)
    return execution

def get_execution_status(
        db: Session,
        execution_id: int
            ) -> Execution:
    execution = db.get(Execution, execution_id)
    if not execution:
        raise ValueError("Execução não encontrada")
    return execution