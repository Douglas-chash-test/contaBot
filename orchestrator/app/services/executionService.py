from datetime import UTC, datetime
from typing import Any, Dict

from sqlalchemy import text
from sqlalchemy.orm import Session

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
