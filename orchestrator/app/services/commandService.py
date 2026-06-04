from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.command import Command
from app.models.execution import Execution


def get_command(
        db: Session,
        execution_id: int    
) -> list[Command]:
    
    execution = db.get(Execution, execution_id)

    if not execution:
        raise ValueError("Execução não encontrada")
    
    commands = ( 
    db.query(Command)
    .filter(
        Command.execution_id == execution_id,
        Command.status == "pending",
    )
    .all()
)
    now = datetime.now(UTC)
    for command in commands:
        command.status = "sent"
        command.sent_at = now
    db.commit()
    return commands

