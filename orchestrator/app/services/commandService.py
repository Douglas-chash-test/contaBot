from datetime import UTC, datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.command import Command
from app.models.execution import Execution
from app.schemas.commandSchema import CommandCreate, CommandResultCreate


def create_command(
        db: Session,
        Payload: CommandCreate
)-> Command:
    execution = db.get(Execution, Payload.execution_id)
    if not execution :
        raise ValueError('A execução relacionada ao comando a ser criado não existe!!')
    command = Command(
        execution_id=Payload.execution_id,
        type=Payload.type,
        payload=Payload.payload,
        status=Payload.status,
        sent_at=datetime.now(UTC)
    )
    db.add(command)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError(
            "Erro ao criar comando"
        ) from exc

    db.refresh(command)
    return command


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

