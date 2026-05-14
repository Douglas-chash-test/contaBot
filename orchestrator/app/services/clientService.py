from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.client import Client
from app.schemas.clientSchema import ClientCreate


def create_client(db: Session, payload: ClientCreate) -> Client:
    client = Client(
        cnpj=payload.cnpj,
        inscricao_estadual=payload.inscricao_estadual,
        razao_social=payload.razao_social,
        whatsapp_dest=payload.whatsapp_dest,
        api_key_hash="temporary",
        erp_type=payload.erp_type,
        db_type=payload.db_type,
        document_types=list(payload.document_types),
        config_json=payload.config_json,
    )
    existing_client = db.execute(
        text("""Select id
         from clients 
         where clients.cnpj = :cnpj 
         or clients.inscricao_estadual = :inscricao_estadual"""),
        {"cnpj": payload.cnpj, "inscricao_estadual": payload.inscricao_estadual},
    ).scalar_one_or_none()

    if existing_client:
        raise ValueError("O Cnpj ou inscrição estadual ja existe na base de dados")

    db.add(client)
    db.commit()
    db.refresh(client)

    return client
