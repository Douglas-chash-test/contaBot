from datetime import UTC, datetime
from typing import Any, Dict, cast

from fastapi import UploadFile
from minio import Minio
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from app.models.execution import Execution
from app.schemas.executionSchema import ExecutionStart


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
    db: Session, minio_client: Minio, execution_id: int, files: list[UploadFile]
) -> Execution:
    execution = db.get(Execution, execution_id)
    if not execution:
        raise ValueError("Execução não encontrada")
    if execution.status != "em_progresso":
        raise ValueError("Execução não está em progresso")

    diagnostico = cast(dict[str, object], execution.log_json.get("diagnostico", {}))
    esperado = int(cast(int, diagnostico.get("total_notas", 0)))
    if esperado != len(files):
        raise ValueError(
            f"Quantidade de XMLs recebidos ({len(files)}) "
            f"não corresponde ao total de notas ({esperado})"
        )

    for file in files:
        filename = file.filename or ""
        if not filename.endswith(".xml"):
            raise ValueError(f"Arquivo {filename} não é um XML")

    storage_path = f"{execution.client_id}/{execution.periodo}/xmls/"

    for file in files:
        minio_client.put_object(
            bucket_name="contabot",
            object_name=f"{storage_path}{file.filename}",
            data=file.file,
            length=-1,
            part_size=10 * 1024 * 1024,
        )
    log_atual = execution.log_json or {}
    log_atual["xmls"] = {"total_recebidos": len(files), "storage_path": storage_path}
    execution.log_json = log_atual
    flag_modified(execution, "log_json")
    db.commit()
    db.refresh(execution)
    return execution
