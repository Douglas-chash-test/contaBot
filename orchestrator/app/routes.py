from typing import Annotated, Any, Dict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.controllers.clientController import create_client_controller
from app.controllers.executionController import (
    create_diagnose_controller,
    create_execution_controller,
)
from app.controllers.raizController import raiz
from app.controllers.testeController import teste_api, teste_db
from app.db.dependencies import get_db
from app.schemas.clientSchema import ClientCreate, ClientRead
from app.schemas.executionSchema import ExecutionDiagnose, ExecutionRead, ExecutionStart

routes = APIRouter()

DbSession = Annotated[Session, Depends(get_db)]


@routes.get("/")
def render_raiz() -> dict[str, str]:
    return raiz()


@routes.get("/teste")
def render_teste_api() -> dict[str, str]:
    return teste_api()


@routes.get("/teste/db")
def render_teste_db(db: DbSession) -> dict[str, str]:
    return teste_db(db)


@routes.post("/clients")
def render_create_client(db: DbSession, payload: ClientCreate) -> ClientRead:
    return create_client_controller(db, payload)


@routes.post("/executions/start")
def render_create_execution(db: DbSession, payload: ExecutionStart) -> ExecutionRead:
    return create_execution_controller(db, payload)


@routes.post("/executions/{execution_id}/diagnose")
def render_create_diagnose(
    db: DbSession, execution_id: int, log_json: Dict[str, Any]
) -> ExecutionDiagnose:
    return create_diagnose_controller(db, execution_id, log_json)
