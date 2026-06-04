from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.commandSchema import (
    CommandRead,
)
from app.services.commandService import (
    get_command,
)


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