from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.clientSchema import ClientCreate, ClientRead
from app.services.clientService import create_client


def create_client_controller(db: Session, payload: ClientCreate) -> ClientRead:
    try:
        client = create_client(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e

    return ClientRead.model_validate(
        {
            "id": client.id,
            "cnpj": client.cnpj,
            "inscricao_estadual": client.inscricao_estadual,
            "razao_social": client.razao_social,
            "whatsapp_dest": client.whatsapp_dest,
            "erp_type": client.erp_type,
            "db_type": client.db_type,
            "document_types": client.document_types,
            "config_json": client.config_json,
        }
    )
