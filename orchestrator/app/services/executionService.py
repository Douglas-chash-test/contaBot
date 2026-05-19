from datetime import UTC, datetime

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
