from typing import Annotated, Any, Dict

from fastapi import APIRouter, Depends, File, UploadFile
from minio import Minio
from sqlalchemy.orm import Session

from app.controllers.clientController import create_client_controller
from app.controllers.commandController import (
    command_result_controller,
    get_command_controller,
)
from app.controllers.executionController import (
    create_diagnose_controller,
    create_execution_controller,
    fail_execution_controller,
    get_execution_status_controller,
    upload_reports_controller,
    upload_xmls_controller,
)
from app.controllers.raizController import raiz
from app.controllers.testeController import teste_api, teste_db
from app.db.dependencies import get_db, get_minio
from app.schemas.clientSchema import ClientCreate, ClientRead
from app.schemas.commandSchema import (
    CommandRead,
    CommandResultCreate,
    CommandResultRead,
)
from app.schemas.executionSchema import (
    ExecutionDiagnose,
    ExecutionFailureCreate,
    ExecutionFailureRead,
    ExecutionRead,
    ExecutionReportsRead,
    ExecutionStart,
    ExecutionStatusGet,
    ExecutionXmlsRead,
)

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


MinioClient = Annotated[Minio, Depends(get_minio)]


@routes.post("/executions/{execution_id}/xmls")
def render_upload_xmls(
    db: DbSession,
    minio_client: MinioClient,
    execution_id: int,
    file: list[UploadFile] = File(...),
) -> ExecutionXmlsRead:
    return upload_xmls_controller(db, minio_client, execution_id, file)

@routes.post("/executions/{execution_id}/reports")
def render_upload_reports(
    db: DbSession,
    minio_client: MinioClient,
    execution_id: int,
    file: list[UploadFile] = File(...),
) -> ExecutionReportsRead:
    return upload_reports_controller(db, minio_client, execution_id, file)

@routes.post("/executions/{execution_id}/failure")
def render_fail_execution(
    db: DbSession,
    execution_id: int,
    payload: ExecutionFailureCreate
) -> ExecutionFailureRead:
    return fail_execution_controller(db, execution_id, payload)

@routes.get("/executions/{execution_id}/status")
def render_execution_status(
    db: DbSession,
    execution_id: int
) -> ExecutionStatusGet:
    return get_execution_status_controller(db, execution_id)

@routes.get("/executions/{execution_id}/commands")
def render_get_command(
    db:DbSession,
    execution_id: int
) -> list[CommandRead]:
    return get_command_controller(db,execution_id)

@routes.post("/commands/{command_id}/result")
def render_command_result(
    db: DbSession,
    command_id: int,
    payload: CommandResultCreate
) -> CommandResultRead:
    return command_result_controller(db, command_id, payload)
