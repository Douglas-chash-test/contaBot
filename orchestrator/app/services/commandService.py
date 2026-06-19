from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.command import Command
from app.models.execution import Execution
from app.schemas.commandSchema import CommandResultCreate


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

def command_result(
        db: Session,
        command_id: int,
        payload: CommandResultCreate
        ) -> Command:
    command = db.get(Command, command_id)
    if not command:
        raise ValueError("Comando não encontrado")
    
    if not command.status == "sent":
        raise ValueError("Comando não está em status 'sent'")
    
    command.status = "executed" if payload.success else "failed"
    command.result_json = payload.model_dump()
    command.executed_at = datetime.now(UTC)

    db.commit()
    db.refresh(command)

    return command

