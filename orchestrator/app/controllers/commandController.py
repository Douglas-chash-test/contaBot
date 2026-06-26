from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.commandSchema import (
    CommandCreate,
    CommandRead,
    CommandResultCreate,
    CommandResultRead,
)
from app.services.commandService import command_result, create_command, get_command


def get_command_controller(db: Session, execution_id: int) -> list[CommandRead]:
    try:
        commands = get_command(db, execution_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return[
        CommandRead.model_validate(
         {
            "id": command.id,
            "execution_id": command.execution_id,
            "type": command.type,
            "payload": command.payload,
            "status": command.status,
            "sent_at": command.sent_at,
         } )
        for command in commands
         ]

def command_create_controller(
        db: Session,
        Payload: CommandCreate
)-> CommandRead:
    try:
        command = create_command(db, Payload)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e), 
        )from e
    return CommandRead.model_validate(
        {
        "id":command.id,
        "execution_id":command.execution_id,
        "type":command.type,
        "payload":command.payload,
        "status":command.status,
        "sent_at":command.sent_at
        }
    )

def command_result_controller(
        db: Session,
        command_id: int,
        payload: CommandResultCreate
) -> CommandResultRead:
    try:
        command = command_result(db, command_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e), 
    )from e
    return CommandResultRead.model_validate(
        {
            "id": command.id,
            "execution_id": command.execution_id,
            "status": command.status,
            "result_json": command.result_json,
            "executed_at": command.executed_at,
        }
    )
